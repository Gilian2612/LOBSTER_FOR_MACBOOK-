import sounddevice as sd
import soundfile as sf
import numpy as np
import queue
import os
import time
from datetime import datetime

# ── Configuración ──────────────────────────────
DEVICE_INDEX   = 4        # BlackHole 2ch — verificar con sd.query_devices()
SAMPLE_RATE    = 16000
CHANNELS       = 1        # CORREGIDO: mono, BlackHole 2ch lo soporta
CHUNK_SEGUNDOS = 30
OUTPUT_DIR     = os.path.expanduser("~/lobster/audio_chunks")
# ───────────────────────────────────────────────

os.makedirs(OUTPUT_DIR, exist_ok=True)
audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"[grabador] ⚠️ Advertencia de stream: {status}")
    audio_queue.put(indata.copy())

def guardar_chunk(datos, indice):
    timestamp = datetime.now().strftime("%H%M%S")
    nombre = f"{OUTPUT_DIR}/chunk_{indice:04d}_{timestamp}.wav"
    if datos.ndim == 2 and datos.shape[1] == 1:
        datos = datos[:, 0]
    sf.write(nombre, datos, SAMPLE_RATE)
    print(f"[grabador] ✅ Guardado: {nombre}")
    return nombre

def iniciar():
    print("[grabador] 🦞 Iniciando captura de audio desde BlackHole...")
    indice = 0
    buffer = []

    while True:
        try:
            print(f"[grabador] Abriendo stream en device={DEVICE_INDEX}, "
                  f"{SAMPLE_RATE}Hz, {CHANNELS}ch...")
            with sd.InputStream(device=DEVICE_INDEX,
                                samplerate=SAMPLE_RATE,
                                channels=CHANNELS,
                                callback=callback):
                print("[grabador] ✅ Stream abierto correctamente")
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
            print("\n[grabador] Detenido por el usuario.")
            break
        except Exception as e:
            print(f"[grabador] ❌ Error en stream: {e}")
            print("[grabador] 🔄 Reintentando en 5 segundos...")
            buffer = []
            time.sleep(5)

if __name__ == "__main__":
    iniciar()