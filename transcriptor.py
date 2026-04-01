import whisper
import os
import glob
import time
import numpy as np
import soundfile as sf
from datetime import datetime

# ── Configuración ──────────────────────────────
AUDIO_DIR       = os.path.expanduser("~/lobster/audio_chunks")
TRANSCRIPT_DIR  = os.path.expanduser("~/lobster")
TRANSCRIPT_FILE = os.path.join(TRANSCRIPT_DIR, "transcript.txt")
MODELO_WHISPER  = "small"
IDIOMA          = None

UMBRAL_SILENCIO  = 0.01   # bajar a 0.005 si corta voz real
UMBRAL_NO_SPEECH = 0.6    # prob. mínima de silencio para descartar
# ───────────────────────────────────────────────

print("[transcriptor] 🦞 Cargando modelo Whisper...")
modelo = whisper.load_model(MODELO_WHISPER)
print("[transcriptor] Modelo listo.")

procesados = set()

FRASES_BASURA = {
    "you", "thank you", "thanks", "thanks for watching",
    "thanks for watching!", "thank you.", "you.", "you!",
    "subtitles by", "subtítulos por", "amara.org",
}

def es_silencio(archivo):
    try:
        datos, _ = sf.read(archivo, dtype="float32")
        rms = np.sqrt(np.mean(datos ** 2))
        print(f"[transcriptor] RMS: {rms:.5f} (umbral: {UMBRAL_SILENCIO})")
        return rms < UMBRAL_SILENCIO
    except Exception as e:
        print(f"[transcriptor] ⚠️ Error leyendo audio para RMS: {e}")
        return False

def transcribir_chunk(archivo):
    print(f"[transcriptor] Transcribiendo: {archivo}")
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
        print(f"[transcriptor] 🚫 Alucinación descartada: {repr(texto)}")
        return None
    print(f"[transcriptor] Texto detectado: {repr(texto)}")
    return texto

def guardar_en_transcript(texto):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(TRANSCRIPT_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {texto}\n")
    print(f"[transcriptor] ✅ Guardado en transcript.txt")

def iniciar():
    print("[transcriptor] 🦞 Escuchando nuevos chunks de audio...")
    while True:
        chunks = sorted(glob.glob(f"{AUDIO_DIR}/chunk_*.wav"))
        nuevos = [c for c in chunks if c not in procesados]
        for chunk in nuevos:
            if es_silencio(chunk):
                print(f"[transcriptor] 🔇 Silencio omitido: {chunk}")
                procesados.add(chunk)
                continue
            texto = transcribir_chunk(chunk)
            if texto:
                guardar_en_transcript(texto)
            procesados.add(chunk)
        time.sleep(10)

if __name__ == "__main__":
    iniciar()
