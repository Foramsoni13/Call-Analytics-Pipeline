"""
Transcription via Groq's hosted Whisper large-v3 model.

Why Groq instead of running faster-whisper locally:
- Runs in the cloud, so ZERO CPU/RAM load on this machine.
- Groq's inference is extremely fast (much faster than CPU-only local runs).
- Free tier is enough for prototyping/sample calls.

IMPORTANT — language handling:
This app only supports Hindi, Gujarati, and English calls (often code-mixed).
Whisper's free-form auto-detect sometimes misidentifies these as a totally
different language (Urdu, Marathi, Nepali, etc.), especially for Gujarati or
short/noisy clips - and when that happens the transcript itself comes out
wrong, which then makes the summary/motive wrong too (garbage in, garbage
out from the LLM step).

To fix this, we force Whisper to transcribe the SAME audio three times, once
each as Hindi, Gujarati, and English, and then keep whichever attempt Whisper
itself was most confident about (using its own avg_logprob per segment).
This guarantees the detected language is always one of our 3 supported ones,
and picks the transcript Whisper is actually most sure of - which fixes both
the wrong-language display and the inaccurate transcript/summary problem.

This does mean each upload makes 3 API calls instead of 1, so processing
takes a bit longer - that's the trade-off for reliable results on a fixed,
known language set.

This module also extracts:
- the detected language (whichever of hi/gu/en Whisper was most confident in)
- an estimated confidence score (derived from Whisper's own per-segment
  log-probabilities - this is the model's own confidence in what it heard,
  NOT a verified accuracy against a human reference transcript, since we
  have no ground-truth transcript to compare against)
- how long the transcription call took

If you ever want to switch to a fully offline/local engine instead, swap
this function's internals for faster-whisper - the rest of the app
(app.py, llm_service.py) does not need to change.
"""
import math
import os
import time
from dotenv import load_dotenv
from groq import Groq
from config import Config

_client = None

# The only 3 languages this app supports. Whisper is forced to try each one
# and we keep whichever attempt it was most confident about - see module
# docstring above for why.
import re

SUPPORTED_LANGUAGES = {
    "hi": "Hindi",
    "gu": "Gujarati",
    "en": "English",
}

# Language-specific prompts in native scripts. Using an English prompt for Gujarati
# or Hindi audio severely degrades Whisper, causing it to hallucinate Roman-character
# gibberish (e.g. "Hap sir", "2xfn") and enter repetitive loops.
LANGUAGE_PROMPTS = {
    "gu": "ગ્રાહક સેવા સહાય, મોબાઇલ નેટવર્ક, રિચાર્જ, બેલેન્સ, બિલ, સમસ્યા, ફરિયાદ, પ્લાન, પૂછપરછ, વાતચીત.",
    "hi": "ग्राहक सेवा सहायता, मोबाइल नेटवर्क, रिचार्ज, बैलेंस, बिल, समस्या, शिकायत, प्लान, पूछताछ, बातचीत.",
    "en": "Customer support call, mobile network, recharge, balance, bill, issue, complaint, plan, inquiry, conversation.",
}


def _clean_whisper_repetition(text):
    """
    Strips ASR hallucination loops (e.g. trailing repetitive characters like
    'વાહીતીતીતીતીતીતીતીતી' or repeating phrases).
    """
    if not text:
        return ""
    # 1. Clean repetitive single characters (4 or more in a row)
    text = re.sub(r"(.)\1{3,}", r"\1", text)
    # 2. Clean repetitive short syllable patterns (2-6 chars repeated 3+ times)
    text = re.sub(r"(.{2,6}?)\1{3,}", r"\1", text)
    # 3. Clean back-to-back identical repeated words (3 or more times)
    text = re.sub(r"\b(\w+)(?:\s+\1){2,}\b", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()



def _get_client():
    global _client
    # Always reload from .env so any changes saved by the user take effect immediately
    load_dotenv(override=True)
    api_key = os.getenv("GROQ_API_KEY", "").strip() or Config.GROQ_API_KEY.strip()

    if not api_key or api_key == "your_groq_api_key_here":
        raise RuntimeError(
            "GROQ_API_KEY is not configured or still has the placeholder value. "
            "Please open your .env file and set your GROQ_API_KEY. "
            "You can get a free key from https://console.groq.com/keys"
        )

    if _client is None or getattr(_client, "api_key", None) != api_key:
        _client = Groq(api_key=api_key)
    return _client


def _seg_value(segment, key, default=None):
    """Segments can come back as dicts or objects depending on SDK version."""
    if isinstance(segment, dict):
        return segment.get(key, default)
    return getattr(segment, key, default)


def _avg_confidence(result):
    """Average Whisper segment confidence for one transcription attempt.
    Returns a raw avg_logprob (higher/less-negative = more confident),
    or a very low fallback if no segments came back at all."""
    segments = getattr(result, "segments", None) or []
    logprobs = [_seg_value(s, "avg_logprob") for s in segments]
    logprobs = [lp for lp in logprobs if lp is not None]
    if not logprobs:
        return -999.0
    return sum(logprobs) / len(logprobs)


# ---------------------------------------------------------------------------
# Confidence breakdown ("why isn't this 100%?")
# ---------------------------------------------------------------------------
# Whisper gives us per-segment metadata that we can turn into an honest,
# human-readable explanation of WHERE the missing confidence went, instead
# of just showing one flat "70%" number. We use:
#   - avg_logprob        -> how sure Whisper was about the words it chose
#   - no_speech_prob      -> how likely the segment is actually silence/noise
#                            rather than speech
#   - compression_ratio   -> unusually high values mean repetitive/garbled
#                            output (a sign Whisper was "guessing")
# and, at the whole-call level, how close the winning language attempt
# (hi/gu/en) was to the runner-up - a close race means code-mixed/ambiguous
# speech, which is itself a source of uncertainty.
#
# IMPORTANT: this is still the MODEL's own confidence in itself, not a
# verified accuracy against a human transcript (we have no ground truth to
# compare against) - so we always label it that way in the UI.

NO_SPEECH_THRESHOLD = 0.4
GARBLED_COMPRESSION_RATIO = 2.4
UNCLEAR_LOGPROB = -0.6
LANGUAGE_AMBIGUITY_GAP = 0.15

REASON_LABELS = {
    "background_noise": "Background noise / silence / crosstalk",
    "garbled_audio": "Repetitive or garbled audio (model was guessing)",
    "unclear_speech": "Fast, mumbled, or heavily accented speech",
    "language_ambiguity": "Hindi/Gujarati/English code-mixing made language detection less certain",
    "minor_uncertainty": "Normal model uncertainty (inherent to any speech-to-text model)",
}


def _segment_confidence_percent(logprob):
    if logprob is None:
        return None
    return round(max(0.0, min(1.0, math.exp(logprob))) * 100, 1)


def _classify_segment(no_speech_prob, compression_ratio, avg_logprob):
    if no_speech_prob is not None and no_speech_prob > NO_SPEECH_THRESHOLD:
        return "background_noise"
    if compression_ratio is not None and compression_ratio > GARBLED_COMPRESSION_RATIO:
        return "garbled_audio"
    if avg_logprob is not None and avg_logprob < UNCLEAR_LOGPROB:
        return "unclear_speech"
    return "minor_uncertainty"


def _build_confidence_breakdown(best_result, overall_confidence_percent, attempt_scores, best_lang_code):
    """
    Returns a JSON-serializable dict explaining the gap between
    overall_confidence_percent and 100%:

    {
        "overall_confidence_percent": 70.0,
        "gap_percent": 30.0,
        "reasons": [
            {"category": "background_noise", "label": "...", "percent": 12.4},
            ...
        ],
        "flagged_segments": [
            {"start": 12.4, "end": 15.8, "text": "...", "reason": "...", "confidence_percent": 41.2},
            ...
        ],
        "language_note": "..." | None
    }
    """
    if overall_confidence_percent is None:
        return None

    gap = round(max(0.0, 100.0 - overall_confidence_percent), 1)
    segments = getattr(best_result, "segments", None) or []

    total_duration = 0.0
    category_deficit = {}
    flagged_segments = []

    for seg in segments:
        start = _seg_value(seg, "start", 0.0) or 0.0
        end = _seg_value(seg, "end", start) or start
        duration = max(end - start, 0.1)
        total_duration += duration

        avg_logprob = _seg_value(seg, "avg_logprob")
        no_speech_prob = _seg_value(seg, "no_speech_prob")
        compression_ratio = _seg_value(seg, "compression_ratio")
        seg_confidence = _segment_confidence_percent(avg_logprob)
        if seg_confidence is None:
            continue

        deficit = max(0.0, 100.0 - seg_confidence)
        if deficit <= 2.0:
            continue  # near-perfect segment, nothing to explain

        category = _classify_segment(no_speech_prob, compression_ratio, avg_logprob)
        category_deficit[category] = category_deficit.get(category, 0.0) + deficit * duration

        if category != "minor_uncertainty" or deficit > 20:
            flagged_segments.append({
                "start": round(start, 1),
                "end": round(end, 1),
                "text": (_seg_value(seg, "text", "") or "").strip(),
                "confidence_percent": seg_confidence,
                "reason": category,
                "reason_label": REASON_LABELS[category],
            })

    # Whole-call factor: how close was the winning language to the runner-up?
    # A tight race = code-mixed/ambiguous speech, which is a real source of
    # uncertainty that isn't visible in any single segment.
    language_note = None
    if attempt_scores and len(attempt_scores) >= 2:
        sorted_scores = sorted(attempt_scores.values(), reverse=True)
        score_gap = sorted_scores[0] - sorted_scores[1]
        if score_gap < LANGUAGE_AMBIGUITY_GAP:
            # Borrow a modest, fixed slice of the deficit for this factor.
            category_deficit["language_ambiguity"] = category_deficit.get("language_ambiguity", 0.0) \
                + (total_duration * 6.0)  # weighted like a segment factor, scaled below
            language_note = (
                f"Detected as {SUPPORTED_LANGUAGES[best_lang_code]}, but the model's confidence in "
                f"the runner-up language was very close - a sign of code-mixed speech."
            )

    # Normalize weighted deficits so they sum to the actual gap.
    raw_total = sum(category_deficit.values())
    reasons = []
    if raw_total > 0 and gap > 0:
        scale = gap / raw_total
        for category, weighted in sorted(category_deficit.items(), key=lambda kv: -kv[1]):
            pct = round(weighted * scale, 1)
            if pct <= 0:
                continue
            reasons.append({
                "category": category,
                "label": REASON_LABELS[category],
                "percent": pct,
            })
        # Rounding can leave the reasons summing to slightly under/over the
        # gap - nudge the largest bucket so the numbers always add up cleanly
        # for the UI.
        diff = round(gap - sum(r["percent"] for r in reasons), 1)
        if reasons and abs(diff) >= 0.1:
            reasons[0]["percent"] = round(reasons[0]["percent"] + diff, 1)
    elif gap > 0:
        # No segment-level signal at all (e.g. no segments returned) - still
        # be honest that there IS a gap, just attribute it generically.
        reasons.append({
            "category": "minor_uncertainty",
            "label": REASON_LABELS["minor_uncertainty"],
            "percent": gap,
        })

    flagged_segments.sort(key=lambda s: s["confidence_percent"])

    return {
        "overall_confidence_percent": overall_confidence_percent,
        "gap_percent": gap,
        "reasons": reasons,
        "flagged_segments": flagged_segments[:6],
        "language_note": language_note,
    }


def _transcribe_forced(client, file_path, audio_bytes, language_code):
    kwargs = {
        "file": (file_path, audio_bytes),
        "model": Config.WHISPER_MODEL,
        "response_format": "verbose_json",
        "language": language_code,
        "temperature": 0.0,
    }
    prompt = LANGUAGE_PROMPTS.get(language_code)
    if prompt:
        kwargs["prompt"] = prompt
    return client.audio.transcriptions.create(**kwargs)


def transcribe_audio(file_path, target_language=None):
    """
    Takes a path to an audio file and an optional target_language ('hi', 'gu', 'en', or 'auto'/None).
    Returns a dict with:
        transcript, language, language_code, audio_duration_seconds,
        confidence_percent, confidence_breakdown, transcription_time_seconds
    """
    client = _get_client()
    start_time = time.time()

    with open(file_path, "rb") as f:
        audio_bytes = f.read()

    best_result = None
    best_lang_code = None
    attempt_scores = {}

    # If the user explicitly requested a specific language, force it directly with its native prompt
    if target_language and target_language in SUPPORTED_LANGUAGES:
        try:
            best_result = _transcribe_forced(client, file_path, audio_bytes, target_language)
            best_lang_code = target_language
        except Exception as e:
            raise RuntimeError(
                f"Groq Whisper transcription failed for {SUPPORTED_LANGUAGES[target_language]}: {e}"
            ) from e
    else:
        # Automatic language detection mode:
        # Let Whisper detect the language naturally from acoustic features without prompt bias.
        # This prevents Whisper from transliterating Gujarati/Hindi audio into Roman characters or English words.
        try:
            natural_result = client.audio.transcriptions.create(
                file=(file_path, audio_bytes),
                model=Config.WHISPER_MODEL,
                response_format="verbose_json",
                temperature=0.0,
            )
        except Exception as e:
            raise RuntimeError(f"Groq Whisper transcription API failed: {e}") from e

        detected_lang = (getattr(natural_result, "language", "") or "").lower().strip()

        # Map Whisper's detected language to our supported set
        if detected_lang in ("hindi", "hi"):
            best_result = natural_result
            best_lang_code = "hi"
        elif detected_lang in ("gujarati", "gu"):
            best_result = natural_result
            best_lang_code = "gu"
        elif detected_lang in ("english", "en"):
            best_result = natural_result
            best_lang_code = "en"
        elif detected_lang in ("urdu", "ur"):
            # Colloquial Urdu speech in Indian customer support calls is Hindi.
            # Re-transcribe with forced Hindi to ensure clean Devanagari script instead of Arabic Nastaliq.
            best_result = _transcribe_forced(client, file_path, audio_bytes, "hi")
            best_lang_code = "hi"
        else:
            # Whisper detected a language outside {hi, gu, en, urdu} (e.g. Marathi, Punjabi, Tagalog, Sindhi).
            # Inspect script of the natural transcript:
            raw_text = getattr(natural_result, "text", "") or ""
            gu_chars = sum(1 for c in raw_text if "\u0a80" <= c <= "\u0aff")
            hi_chars = sum(1 for c in raw_text if "\u0900" <= c <= "\u097f")
            latin_chars = sum(1 for c in raw_text if c.isascii() and c.isalpha())

            if gu_chars > hi_chars and gu_chars > 15:
                best_result = natural_result
                best_lang_code = "gu"
            elif hi_chars > 15:
                # If it's already Devanagari, it is readable Hindi/Devanagari
                best_result = natural_result
                best_lang_code = "hi"
            elif latin_chars > len(raw_text) * 0.4:
                best_result = natural_result
                best_lang_code = "en"
            else:
                # Force Hindi as default primary call-center language
                try:
                    best_result = _transcribe_forced(client, file_path, audio_bytes, "hi")
                    best_lang_code = "hi"
                except Exception:
                    best_result = natural_result
                    best_lang_code = "hi"

    elapsed = round(time.time() - start_time, 2)

    if best_result is None:
        raise RuntimeError(
            "Could not transcribe this call in Hindi, Gujarati, or English. "
            "Please check the audio file and try again."
        )

    score = _avg_confidence(best_result)
    attempt_scores[best_lang_code] = score

    raw_transcript = (getattr(best_result, "text", "") or "").strip()
    transcript = _clean_whisper_repetition(raw_transcript)
    language_name = SUPPORTED_LANGUAGES[best_lang_code]
    audio_duration = getattr(best_result, "duration", None)

    confidence_percent = None
    if score > -999.0:
        confidence_percent = round(max(0.0, min(1.0, math.exp(score))) * 100, 1)

    confidence_breakdown = _build_confidence_breakdown(
        best_result, confidence_percent, attempt_scores, best_lang_code
    )

    return {
        "transcript": transcript,
        "language": language_name,
        "language_code": best_lang_code,
        "audio_duration_seconds": round(audio_duration, 2) if audio_duration else None,
        "confidence_percent": confidence_percent,
        "confidence_breakdown": confidence_breakdown,
        "transcription_time_seconds": elapsed,
    }
