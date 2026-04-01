import os
import time
import requests
from datetime import datetime
from config import (
    TRANSCRIPT_FILE, RESPUESTAS_FILE, PALABRA_CLAVE,
    OLLAMA_URL, MODELO_OLLAMA, CONTEXTO_LINEAS, OLLAMA_TIMEOUT
)
from logger import get_logger

# ── Setup ───────────────────────────────────────
log = get_logger("detector")
# ───────────────────────────────────────────────

def obtener_contexto():
    if not os.path.exists(TRANSCRIPT_FILE):
        return ""
    with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    return "".join(lineas[-CONTEXTO_LINEAS:])

def preguntar_a_ollama(pregunta, contexto):
    prompt = f"""Eres un asistente de reuniones llamado Lobster.
Aqui esta la transcripcion reciente de la reunion:

{contexto}

Un participante pregunto: {pregunta}

Responde de forma concisa y util en el mismo idioma de la pregunta."""

    log.info(f"Consultando a Ollama — pregunta: {repr(pregunta)}")
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODELO_OLLAMA, "prompt": prompt, "stream": False},
            timeout=OLLAMA_TIMEOUT
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.Timeout:
        log.error("Ollama no respondió en el tiempo límite")
        return "Lo siento, el modelo tardó demasiado en responder."
    except requests.ConnectionError:
        log.error("No se pudo conectar a Ollama — ¿está corriendo?")
        return "Lo siento, no pude conectarme al modelo."
    except Exception as e:
        log.error(f"Error inesperado consultando Ollama: {e}")
        return "Lo siento, ocurrió un error al procesar tu pregunta."

def guardar_respuesta(pregunta, respuesta):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(RESPUESTAS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}] PREGUNTA: {pregunta}\n")
        f.write(f"[{timestamp}] LOBSTER: {respuesta}\n")
        f.write("-" * 50 + "\n")
    log.info("Respuesta guardada en respuestas.txt")

def iniciar():
    log.info("🦞 Escuchando por Hey Lobster...")
    ultima_linea = 0

    while True:
        if os.path.exists(TRANSCRIPT_FILE):
            with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
                lineas = f.readlines()

            nuevas = lineas[ultima_linea:]
            for linea in nuevas:
                if PALABRA_CLAVE in linea.lower():
                    partes = linea.lower().split(PALABRA_CLAVE, 1)
                    pregunta = partes[1].strip() if len(partes) > 1 else "resume la reunion"
                    contexto = obtener_contexto()
                    respuesta = preguntar_a_ollama(pregunta, contexto)
                    log.info(f"LOBSTER DICE: {respuesta}")
                    guardar_respuesta(pregunta, respuesta)

            ultima_linea = len(lineas)

        time.sleep(5)

if __name__ == "__main__":
    iniciar()