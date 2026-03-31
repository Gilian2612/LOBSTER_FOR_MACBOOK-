import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import queue
import os
from datetime import datetime

# ── Configuración ──────────────────────────────
DEVICE_INDEX = 4          # BlackHole 2ch
SAMPLE_RATE  = 16000      # Whisper prefiere 16kHz
CHANNELS     = 3          # Mono es suficiente
CHUNK_SEGUNDOS = 30       # Graba bloques de 30 segundos
OUTPUT_DIR   = os.path.expanduser("~/lobster/audio_chunks")
# ───────────────────────────────────────────────

os.makedirs(OUTPUT_DIR, exist_ok=True)
audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"[grabador] Advertencia: {status}")
    audio_queue.put(indata.copy())

def guardar_chunk(datos, indice):
    timestamp = datetime.now().strftime("%H%M%S")
    nombre = f"{OUTPUT_DIR}/chunk_{indice:04d}_{timestamp}.wav"
    sf.write(nombre, datos, SAMPLE_RATE)
    print(f"[grabador] Guardado: {nombre}")
    return nombre

def iniciar():
    print("[grabador] 🦞 Iniciando captura de audio desde BlackHole...")
    indice = 0
    buffer = []

    with sd.InputStream(device=DEVICE_INDEX,
                        samplerate=SAMPLE_RATE,
                        channels=CHANNELS,
                        callback=callback):
        while True:
            try:
                data = audio_queue.get(timeout=1)
                buffer.append(data)

                duracion = len(buffer) * 1024 / SAMPLE_RATE
                if duracion >= CHUNK_SEGUNDOS:
                    datos_completos = np.concatenate(buffer, axis=0)
                    guardar_chunk(datos_completos, indice)
                    indice += 1
                    buffer = []

            except queue.Empty:
                continue
            except KeyboardInterrupt:
                print("\n[grabador] Detenido.")
                break

if __name__ == "__main__":
    iniciar()
