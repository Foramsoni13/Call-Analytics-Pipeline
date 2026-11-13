"""
End-to-end orchestration for a single uploaded call.

This is the ONE place that knows the full pipeline order and wires the
other services together:

    preprocess_audio -> transcribe_audio -> analyze_transcript (classify
    + extract structured data) -> save everything to MongoDB

Why this exists as its own module instead of living inline in app.py:
- app.py's route handler stays a thin HTTP layer (save file, call
  run_pipeline, redirect) instead of knowing about audio cleanup, Whisper,
  or the LLM.
- The call's `status` field in MongoDB is updated after EVERY stage, not
  just once at the end - so the dashboard always shows exactly where a
  call is (preprocessing / transcribing / analyzing / completed / failed)
  instead of one opaque "processing" flag the whole time.
- If a stage fails, we know exactly which stage it was (`failed_stage`)
  and we keep whatever earlier stages already produced instead of losing
  it - e.g. a transcript is still saved and viewable even if the
  classification step errors out afterwards.
- Temp files created during preprocessing are always cleaned up (success
  or failure) via `finally`.
"""
import time
import traceback
from datetime import datetime, timezone

from services.audio_processing import preprocess_audio, cleanup_temp_audio
from services.transcription_service import transcribe_audio
from services.llm_service import analyze_transcript, extract_phone_numbers


def _update(calls_collection, call_id, fields):
    calls_collection.update_one({"_id": call_id}, {"$set": fields})


def run_pipeline(calls_collection, call_id, file_path, filename, target_language="auto"):
    """
    Runs the full preprocess -> transcribe -> analyze pipeline for one
    uploaded call, writing progress and final results to MongoDB as it
    goes.

    Returns (success: bool, error_message: str | None).
    """
    pipeline_start = time.time()
    cleaned_path = file_path
    is_temp_file = False

    try:
        # ---- stage 1: audio preprocessing (noise reduction, etc.) ----
        _update(calls_collection, call_id, {"status": "preprocessing_audio"})
        try:
            cleaned_path, is_temp_file = preprocess_audio(file_path)
        except Exception:
            # Preprocessing is a best-effort accuracy boost, not a hard
            # requirement - if it blows up, fall back to the raw upload
            # instead of failing the whole call.
            traceback.print_exc()
            cleaned_path, is_temp_file = file_path, False

        # ---- stage 2: speech-to-text ----
        _update(calls_collection, call_id, {"status": "transcribing"})
        transcription_result = transcribe_audio(cleaned_path, target_language=target_language)

        _update(calls_collection, call_id, {
            "status": "analyzing",
            "transcript": transcription_result["transcript"],
            "language": transcription_result["language"],
            "confidence_percent": transcription_result["confidence_percent"],
            "confidence_breakdown": transcription_result["confidence_breakdown"],
            "audio_duration_seconds": transcription_result["audio_duration_seconds"],
            "transcription_time_seconds": transcription_result["transcription_time_seconds"],
        })

        # ---- stage 3: classification + structured data extraction + translation ----
        analysis = analyze_transcript(
            transcription_result["transcript"],
            language_name=transcription_result["language"]
        )
        phone_numbers = extract_phone_numbers(transcription_result["transcript"])

        total_time = round(time.time() - pipeline_start, 2)

        _update(calls_collection, call_id, {
            "status": "completed",
            "summary": analysis.get("summary"),
            "motive": analysis.get("motive"),
            "summary_english": analysis.get("summary_english"),
            "motive_english": analysis.get("motive_english"),
            "category": analysis.get("category"),
            "sentiment": analysis.get("sentiment"),
            "priority": analysis.get("priority"),
            "resolution_status": analysis.get("resolution_status"),
            "customer_name": analysis.get("customer_name"),
            "agent_name": analysis.get("agent_name"),
            "key_issues": analysis.get("key_issues", []),
            "action_items": analysis.get("action_items", []),
            "follow_up_required": analysis.get("follow_up_required", False),
            "phone_numbers_mentioned": phone_numbers,
            "transcript_gujarati": analysis.get("transcript_gujarati"),
            "transcript_hindi": analysis.get("transcript_hindi"),
            "transcript_english": analysis.get("transcript_english"),
            "llm_time_seconds": analysis.get("llm_time_seconds"),
            "total_time_seconds": total_time,
            "completed_at": datetime.now(timezone.utc),
        })

        return True, None

    except Exception as e:
        traceback.print_exc()
        # Figure out which stage we were in when it broke, from what's
        # already on the document, so the UI can say something useful.
        current = calls_collection.find_one({"_id": call_id}, {"status": 1})
        failed_stage = current["status"] if current else "unknown"
        _update(calls_collection, call_id, {
            "status": "failed",
            "failed_stage": failed_stage,
            "error": str(e),
        })
        return False, str(e)

    finally:
        cleanup_temp_audio(cleaned_path, is_temp_file)
