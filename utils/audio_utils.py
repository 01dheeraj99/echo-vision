import os
import re
from pathlib import Path
from gtts import gTTS
import pyttsx3

from config.settings import DEFAULT_TTS_ENGINE, TTS_LANGUAGE, PYTTSX3_RATE, PYTTSX3_VOLUME

def sanitize_text_for_speech(text: str) -> str:
    """Clean up text for natural pronunciation by text-to-speech engines."""
    if not text:
        return "No visual description available."
    # Replace multiple spaces/newlines
    text = re.sub(r"\s+", " ", text).strip()
    return text

def build_accessible_narration(caption: str = "", objects: list = None, ocr_text: str = "") -> str:
    """
    Format a complete, structured, highly accessible spoken description.
    Optimized for clarity when read aloud to visually impaired users.
    """
    parts = []

    # 1. Main Scene Description
    if caption and caption.strip():
        # Capitalize first letter
        clean_cap = caption.strip()
        clean_cap = clean_cap[0].upper() + clean_cap[1:]
        if not clean_cap.endswith("."):
            clean_cap += "."
        parts.append(f"Image summary: {clean_cap}")
    else:
        parts.append("Image summary: Scene could not be identified.")

    # 2. Key Detected Objects
    if objects and len(objects) > 0:
        # Group by label to give clean counts (e.g., "2 cups and 1 laptop")
        counts = {}
        for obj in objects:
            lbl = obj.get("label", "object")
            counts[lbl] = counts.get(lbl, 0) + 1
        
        obj_phrases = []
        for lbl, cnt in counts.items():
            if cnt > 1:
                obj_phrases.append(f"{cnt} {lbl}s")
            else:
                obj_phrases.append(f"1 {lbl}")

        if len(obj_phrases) == 1:
            items_str = obj_phrases[0]
        elif len(obj_phrases) == 2:
            items_str = f"{obj_phrases[0]} and {obj_phrases[1]}"
        else:
            items_str = ", ".join(obj_phrases[:-1]) + f", and {obj_phrases[-1]}"

        parts.append(f"Detected items in view: {items_str}.")

    # 3. Text in Image (OCR)
    if ocr_text and ocr_text.strip():
        parts.append(f"Text detected in image: {ocr_text.strip()}.")

    narration = " ".join(parts)
    return sanitize_text_for_speech(narration)

def text_to_speech(text: str, output_path: str = "data/outputs/output.mp3", engine: str = DEFAULT_TTS_ENGINE) -> dict:
    """
    Converts text to speech audio.
    Supports online gTTS with transparent offline pyttsx3 fallback.
    """
    text = sanitize_text_for_speech(text)
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    used_engine = None

    # Try online gTTS first if auto or gtts
    if engine in ("auto", "gtts"):
        try:
            tts = gTTS(text=text, lang=TTS_LANGUAGE)
            tts.save(output_path)
            used_engine = "gtts"
            print(f"[INFO] gTTS audio generated successfully at: {output_path}")
            return {"success": True, "engine": "gtts", "output_path": output_path, "text": text}
        except Exception as e:
            print(f"[WARN] gTTS online generation failed ({e}). Falling back to pyttsx3 offline engine.")
            if engine == "gtts":
                raise

    # Fallback to offline pyttsx3 (SAPI5 on Windows)
    try:
        # Note: On Windows pyttsx3 typically outputs .wav; saving as mp3 or wav works
        pyttsx_engine = pyttsx3.init()
        pyttsx_engine.setProperty("rate", PYTTSX3_RATE)
        pyttsx_engine.setProperty("volume", PYTTSX3_VOLUME)

        # For pyttsx3 on windows, wav is the native format
        wav_output = output_path
        if output_path.endswith(".mp3"):
            wav_output = output_path[:-4] + ".wav"

        pyttsx_engine.save_to_file(text, wav_output)
        pyttsx_engine.runAndWait()
        used_engine = "pyttsx3"
        print(f"[INFO] pyttsx3 offline audio generated at: {wav_output}")
        return {"success": True, "engine": "pyttsx3", "output_path": wav_output, "text": text}
    except Exception as e:
        print(f"[ERROR] Both TTS engines failed: {e}")
        raise
