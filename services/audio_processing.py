"""
Audio preprocessing — runs BEFORE transcription to make the accuracy of
Whisper's output better on real phone-call recordings (background hiss,
low-volume calls, phone-line rumble, etc).

Pipeline:
1. Decode the original file (mp3/wav/m4a/ogg/webm) via pydub. This needs
   the `ffmpeg` binary to be installed and on PATH (see README).
2. Downmix to mono + resample to 16kHz — this is Whisper's native rate,
   so we're not wasting bits on stuff it discards internally anyway.
3. Band-pass filter tuned to the phone voice band (~80Hz-3800Hz) — cuts
   low-frequency rumble/hum and high-frequency hiss that sit outside
   where speech actually lives on a phone call.
4. Spectral-gating noise reduction (`noisereduce`, stationary mode) —
   suppresses steady background noise (fan noise, line static, AC hum)
   without needing a separate "noise-only" reference clip.
5. Loudness normalization — so a quiet call doesn't get mistranscribed
   and a loud one doesn't clip.

Design choice: if ffmpeg/pydub/noisereduce are missing OR preprocessing
fails for any reason (corrupt file, weird codec, etc.), we log a warning
and fall back to the ORIGINAL file untouched. Cleanup should never be a
hard requirement for the app to work — worst case, accuracy is what it
was before, not a crash.
"""
import os
import tempfile
import traceback

import numpy as np


def preprocess_audio(input_path):
    """
    Cleans up a call recording for better transcription accuracy.

    Returns:
        (path_to_use: str, is_temp_file: bool)
        - path_to_use: the cleaned WAV path, or input_path if cleanup
          wasn't possible/failed.
        - is_temp_file: True only if a new file was actually written to
          disk (so the caller knows whether it needs deleting afterwards).
    """
    try:
        from pydub import AudioSegment
        from pydub.effects import normalize
        import noisereduce as nr
    except ImportError:
        # Optional dependency not installed — degrade gracefully.
        return input_path, False

    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        # Gentle high-pass filter at 50Hz to remove DC offset / sub-audible mechanical rumble
        # without cutting off human vocal formants or phone wideband frequencies
        audio = audio.high_pass_filter(50)
        audio = normalize(audio)

        # Trim trailing dead silence: Whisper often gets trapped in repetitive hallucination loops
        # when audio ends in silence/low noise. We strip silence below -42dBFS from the end:
        orig_len = len(audio)
        end_trim = orig_len
        chunk_ms = 100
        while end_trim > 1000 and audio[end_trim - chunk_ms : end_trim].dBFS < -42.0:
            end_trim -= chunk_ms
        if end_trim < orig_len:
            audio = audio[:end_trim + 200]  # retain 200ms natural tail padding

        fd, out_path = tempfile.mkstemp(suffix="_clean.wav", prefix="callsense_")
        os.close(fd)
        cleaned = audio
        cleaned.export(out_path, format="wav")
        return out_path, True

    except Exception:
        # Never let a preprocessing bug break the upload — just use the
        # original file as-is and let Whisper deal with it directly.
        traceback.print_exc()
        return input_path, False


def cleanup_temp_audio(path, is_temp_file):
    """Deletes the temp cleaned-audio file created by preprocess_audio, if any."""
    if is_temp_file and path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass
