import whisper
import os
import glob
import time
import numpy as np
import soundfile as sf
from datetime import datetime
from config import (
    AUDIO_DIR, TRANSCRIPT_FILE, MODELO_WHISPER, IDIOMA,
    UMBRAL_SILENCIO, UMBRAL_NO_SPEECH
)
from logger import get_logger

# ── Setup ───────────────────────────────────────
log = get_logger("transcriptor")
# ───────────────────────────────────────────────

FRASES_BASURA = {
    "you", "thank you", "thanks", "thanks for watching",
    "thanks for watching!", "thank you.", "you.", "you!",
    "subtitles by", "subtítulos por", "amara.org",
}

log.info("Cargando modelo Whisper...")
modelo = whisper.load_model(MODELO_WHISPER)
log.info("Modelo listo.")

procesados = set()

def es_silencio(archivo):
    try:
        datos, _ = sf.read(archivo, dtype="float32")
        rms = np.sqrt(np.mean(datos ** 2))
        log.debug(f"RMS: {rms:.5f} (umbral: {UMBRAL_SILENCIO})")
        return rms < UMBRAL_SILENCIO
    except Exception as e:
        log.warning(f"No se pudo leer el audio para RMS: {e}")
        return False

def transcribir_chunk(archivo):
    log.info(f"Transcribiendo: {archivo}")
    resultado = modelo.transcribe(
        archivo,
        language=IDIOMA,
        fp16=False,
        no_speech_threshold=UMBRAL_NO_SPEECH,
        suppress_tokens=[50362, 50363, 1770, 13, 1],
        logprob_threshold=-1.0,
        condition_on_previous_text=False,
    )
    texto = resultado["text"].strip()
    if texto.lower() in FRASES_BASURA:
        log.warning(f"Alucinación descartada: {repr(texto)}")
        return None
    log.info(f"Texto detectado: {repr(texto)}")
    return texto

def guardar_en_transcript(texto):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(TRANSCRIPT_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {texto}\n")
    log.info("Guardado en transcript.txt")

def iniciar():
    log.info("🦞 Escuchando nuevos chunks de audio...")
    while True:
        chunks = sorted(glob.glob(f"{AUDIO_DIR}/chunk_*.wav"))
        nuevos = [c for c in chunks if c not in procesados]
        for chunk in nuevos:
            if es_silencio(chunk):
                log.debug(f"Chunk silencioso omitido: {chunk}")
                procesados.add(chunk)
                continue
            texto = transcribir_chunk(chunk)
            if texto:
                guardar_en_transcript(texto)
            procesados.add(chunk)
        time.sleep(10)

if __name__ == "__main__":
    iniciar()