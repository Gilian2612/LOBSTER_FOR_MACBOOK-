import sounddevice as sd
import soundfile as sf
import numpy as np
import queue
import os
import time
from config import (
    DEVICE_INDEX, SAMPLE_RATE, CHANNELS,
    CHUNK_SEGUNDOS, AUDIO_DIR
)
from logger import get_logger

# ── Setup ───────────────────────────────────────
log = get_logger("grabador")
# ───────────────────────────────────────────────

os.makedirs(AUDIO_DIR, exist_ok=True)
audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        log.warning(f"Advertencia de stream: {status}")
    audio_queue.put(indata.copy())

def guardar_chunk(datos, indice):
    from datetime import datetime
    timestamp = datetime.now().strftime("%H%M%S")
    nombre = f"{AUDIO_DIR}/chunk_{indice:04d}_{timestamp}.wav"
    if datos.ndim == 2 and datos.shape[1] == 1:
        datos = datos[:, 0]
    sf.write(nombre, datos, SAMPLE_RATE)
    log.info(f"Guardado: {nombre}")
    return nombre

def iniciar():
    log.info("🦞 Iniciando captura de audio desde BlackHole...")
    indice = 0
    buffer = []

    while True:
        try:
            log.info(f"Abriendo stream — device={DEVICE_INDEX}, "
                     f"{SAMPLE_RATE}Hz, {CHANNELS}ch...")
            with sd.InputStream(device=DEVICE_INDEX,
                                samplerate=SAMPLE_RATE,
                                channels=CHANNELS,
                                callback=callback):
                log.info("Stream abierto correctamente")
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
            log.info("Detenido por el usuario.")
            break
        except Exception as e:
            log.error(f"Error en stream: {e}")
            log.info("Reintentando en 5 segundos...")
            buffer = []
            time.sleep(5)

if __name__ == "__main__":
    iniciar()