import whisper
import os
import glob
import time
from datetime import datetime

# ── Configuración ──────────────────────────────
AUDIO_DIR      = os.path.expanduser("~/lobster/audio_chunks")
TRANSCRIPT_DIR = os.path.expanduser("~/lobster")
TRANSCRIPT_FILE = os.path.join(TRANSCRIPT_DIR, "transcript.txt")
MODELO_WHISPER = "small"        # small = buen balance velocidad/precisión
IDIOMA         = None           # Español
# ───────────────────────────────────────────────

print("[transcriptor] 🦞 Cargando modelo Whisper...")
modelo = whisper.load_model(MODELO_WHISPER)
print("[transcriptor] Modelo listo.")

procesados = set()

def transcribir_chunk(archivo):
    print(f"[transcriptor] Transcribiendo: {archivo}")
    resultado = modelo.transcribe(archivo, language=IDIOMA, fp16=False)
    texto = resultado["text"].strip()
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
            texto = transcribir_chunk(chunk)
            if texto:
                guardar_en_transcript(texto)
            procesados.add(chunk)

        time.sleep(10)

if __name__ == "__main__":
    iniciar()
