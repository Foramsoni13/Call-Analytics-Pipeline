"""
Two things happen in this module, both via Groq's hosted LLM
(llama-3.3-70b-versatile) - this replaces Ollama from the original plan,
runs on Groq's cloud so it doesn't touch local CPU/RAM at all:

1. CLASSIFICATION - category, sentiment, priority, resolution status.
2. DATA EXTRACTION - structured fields pulled out of the free-text
   transcript: customer name, agent name, the customer's key issues,
   concrete action items, and whether a follow-up is needed.

Both are done in a single LLM call (one combined JSON schema) rather than
two separate calls - same accuracy, half the API calls/latency/cost.

Language detection is NOT done here - transcription_service.py already gets
the real detected language straight from Whisper, which is more reliable
than asking an LLM to guess it from text.
"""
import json
import os
import re
import time
from dotenv import load_dotenv
from groq import Groq
from config import Config

_client = None

# Matches a standalone 10-digit Indian mobile/landline number in the
# transcript. This is done with a plain regex (not the LLM) because phone
# numbers are exact digit sequences - a regex will never "hallucinate" a
# digit the way an LLM occasionally can, so it's the more accurate tool
# for this specific job.
_PHONE_RE = re.compile(r"(?<!\d)(\d{10})(?!\d)")


def _get_client():
    global _client
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


def _chat_completion_with_fallback(client, messages):
    configured = os.getenv("LLM_MODEL", "").strip() or Config.LLM_MODEL
    models_to_try = [
        configured,
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b",
    ]
    seen = set()
    models = [m for m in models_to_try if m and not (m in seen or seen.add(m))]

    last_error = None
    for model in models:
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.2,
                max_tokens=4096,
                response_format={"type": "json_object"},
            )
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            if "model" in err_str or "not found" in err_str or "does not exist" in err_str:
                continue
            raise
    if last_error:
        raise last_error


def extract_phone_numbers(transcript):
    """Deterministic regex-based extraction of 10-digit numbers mentioned
    in the transcript (e.g. customer reading out an alternate contact
    number)."""
    if not transcript:
        return []
    return sorted(set(_PHONE_RE.findall(transcript)))


def _build_prompt(transcript, language_name="Hindi"):
    categories = ", ".join(Config.CALL_CATEGORIES)
    priorities = ", ".join(Config.PRIORITY_LEVELS)
    resolutions = ", ".join(Config.RESOLUTION_STATUSES)

    lang_lower = (language_name or "Hindi").lower().strip()
    if lang_lower == "gujarati":
        lang_rule = (
            "CRITICAL LANGUAGE RULE: The call language is GUJARATI. All descriptive fields "
            "('motive', 'summary', 'key_issues', 'action_items', 'customer_name', 'agent_name') "
            "MUST be written in pure, fluent GUJARATI (ગુજરાતી લિપિ). Do not write English in these fields."
        )
        sample_motive = "કૉલનું કારણ (ગુજરાતીમાં 6-10 શબ્દો)"
        sample_summary = "કૉલનો સંપૂર્ણ સારાંશ (ગુજરાતીમાં 2-3 વાક્યો)"
        target_lang_label = "Gujarati"
    elif lang_lower == "hindi":
        lang_rule = (
            "CRITICAL LANGUAGE RULE: The call language is HINDI. All descriptive fields "
            "('motive', 'summary', 'key_issues', 'action_items', 'customer_name', 'agent_name') "
            "MUST be written in pure, fluent HINDI (हिंदी / देवनागरी लिपि). Do not write English in these fields."
        )
        sample_motive = "कॉल का मुख्य कारण (हिंदी में 6-10 शब्द)"
        sample_summary = "कॉल का संपूर्ण सारांश (हिंदी में 2-3 वाक्य)"
        target_lang_label = "Hindi"
    else:
        lang_rule = (
            "CRITICAL LANGUAGE RULE: The call language is ENGLISH. Write all descriptive fields in clear, professional English."
        )
        sample_motive = "Short phrase (6-10 words in English) capturing WHY the customer called"
        sample_summary = "2-3 sentence summary in English of the problem and agent solution"
        target_lang_label = "English"

    return f"""You are an expert multilingual call analytics linguist and assistant.
{lang_rule}

IMPORTANT CONTEXT ON INPUT TRANSCRIPT:
The transcript below was generated by speech-to-text (ASR) from phone audio. It may contain acoustic phonetic mishearings, colloquial pronunciations, or repeated syllables (for example, "ગુડીયુનીયાં" for "ગુડ ઇવનિંગ", "તુનાલ બાજ કરું" for "કુણાલ વાત કરું છું", "સ્લીવ" for "સ્લિપ/સર્વિસ", etc.).

YOUR TASKS:
1. Reconstruct and clean the dialogue into natural, grammatically correct language while faithfully preserving the speakers' intended meaning.
2. For "translation_gujarati": Provide a fluent, complete, grammatically correct Gujarati version (શુદ્ધ અને અર્થપૂર્ણ ગુજરાતી). If the call is already in Gujarati, this should be the reconstructed clean Gujarati transcript free of ASR phonetic mishearings and repetition loops.
3. For "translation_hindi": Provide a fluent, complete, grammatically correct Hindi version in Devanagari script (शुद्ध और स्पष्ट हिंदी). If the call is already in Hindi, this should be the reconstructed clean Hindi transcript free of ASR phonetic mishearings and repetition loops.
4. For "translation_english": Provide a complete, fluent, professional English translation of the conversation. Never write "unintelligible" or dismiss non-English speech as nonsensical — provide the most coherent English translation of what was communicated.
5. Extract structured insights (motive, summary, category, sentiment, priority, etc.) accurately from the reconstructed dialogue.

Return ONLY a valid JSON object with exactly these keys, nothing else:

- "motive": {sample_motive}.
- "summary": {sample_summary}.
- "summary_english": 2-3 sentence summary in English (always provided in English for cross-team reporting).
- "motive_english": short motive in English (6-10 words).
- "category": pick exactly ONE value from: [{categories}]
- "sentiment": one of "Positive", "Neutral", "Negative".
- "priority": how urgently this call needs attention/follow-up - pick exactly ONE value from: [{priorities}]
- "resolution_status": pick exactly ONE value from: [{resolutions}]
- "customer_name": the customer's name if stated (in {target_lang_label}), else null.
- "agent_name": the support agent's name if stated (in {target_lang_label}), else null.
- "key_issues": a list of 1-5 short phrases in {target_lang_label}, each naming one distinct problem raised in the call.
- "action_items": a list of 0-5 short phrases in {target_lang_label} describing concrete next steps/commitments made.
- "follow_up_required": true or false.
- "translation_gujarati": full, natural, grammatically correct Gujarati translation/reconstruction in proper Gujarati script (શુદ્ધ ગુજરાતી).
- "translation_hindi": full, natural, grammatically correct Hindi translation/reconstruction in proper Devanagari script (शुद्ध हिंदी).
- "translation_english": full, natural, fluent English translation of the conversation.

Transcript:
\"\"\"{transcript}\"\"\"
"""


def analyze_transcript(transcript, language_name="Hindi"):
    """
    Sends the transcript to the LLM and returns a parsed dict with
    classification fields (category, sentiment, priority, resolution_status)
    and extracted-data fields (customer_name, agent_name, key_issues,
    action_items, follow_up_required), plus motive/summary/llm_time_seconds,
    where summary, motive, key_issues, and action_items match the call's language.
    """
    client = _get_client()
    start_time = time.time()

    response = _chat_completion_with_fallback(
        client,
        messages=[
            {"role": "system", "content": f"You are a precise JSON-only response generator for a call analytics system. The call language is {language_name}. Generate all insights in {language_name}."},
            {"role": "user", "content": _build_prompt(transcript, language_name=language_name)},
        ],
    )

    elapsed = round(time.time() - start_time, 2)
    raw = response.choices[0].message.content

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        data = {}

    # ---- classification fields: guard against invalid/missing values ----
    if data.get("category") not in Config.CALL_CATEGORIES:
        data["category"] = "Other"
    if data.get("sentiment") not in {"Positive", "Neutral", "Negative"}:
        data["sentiment"] = "Neutral"
    if data.get("priority") not in Config.PRIORITY_LEVELS:
        data["priority"] = "Medium"
    if data.get("resolution_status") not in Config.RESOLUTION_STATUSES:
        data["resolution_status"] = "Unresolved"

    if not data.get("motive"):
        data["motive"] = "Could not be determined."
    if not data.get("summary"):
        data["summary"] = "Summary could not be generated."

    # ---- extracted-data fields: guard against wrong types ----
    if not isinstance(data.get("key_issues"), list):
        data["key_issues"] = []
    if not isinstance(data.get("action_items"), list):
        data["action_items"] = []
    if not isinstance(data.get("follow_up_required"), bool):
        data["follow_up_required"] = False
    if not data.get("customer_name") or not isinstance(data.get("customer_name"), str):
        data["customer_name"] = None
    if not data.get("agent_name") or not isinstance(data.get("agent_name"), str):
        data["agent_name"] = None

    data["summary_english"] = data.get("summary_english") or None
    data["motive_english"] = data.get("motive_english") or None
    data["transcript_gujarati"] = data.get("translation_gujarati") or None
    data["transcript_hindi"] = data.get("translation_hindi") or None
    data["transcript_english"] = data.get("translation_english") or None

    data["llm_time_seconds"] = elapsed
    return data
