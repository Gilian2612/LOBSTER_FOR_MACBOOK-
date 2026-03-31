import os
import time
import requests
from datetime import datetime

# ── Configuración ──────────────────────────────
TRANSCRIPT_FILE  = os.path.expanduser("~/lobster/transcript.txt")
RESPUESTAS_FILE  = os.path.expanduser("~/lobster/respuestas.txt")
PALABRA_CLAVE    = "hey lobster"
OLLAMA_URL       = "http://localhost:11434/api/generate"
MODELO           = "qwen2.5-coder:14b"
CONTEXTO_LINEAS  = 50
# ───────────────────────────────────────────────

procesadas = set()

def obtener_contexto():
    if not os.path.exists(TRANSCRIPT_FILE):
        return ""
    with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    return "".join(lineas[-CONTEXTO_LINEAS:])

def preguntar_a_qwen(pregunta, contexto):
    prompt = f"""Eres un asistente de reuniones llamado Lobster.
Aqui esta la transcripcion reciente de la reunion:

{contexto}

Un participante pregunto: {pregunta}

Responde de forma concisa y util en el mismo idioma de la pregunta."""

    print(f"[detector] Consultando a Qwen...")
    response = requests.post(OLLAMA_URL, json={
        "model": MODELO,
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"]

def guardar_respuesta(pregunta, respuesta):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(RESPUESTAS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}] PREGUNTA: {pregunta}\n")
        f.write(f"[{timestamp}] LOBSTER: {respuesta}\n")
        f.write("-" * 50 + "\n")
    print(f"[detector] Respuesta guardada en respuestas.txt")

def iniciar():
    print("[detector] Escuchando por Hey Lobster...")
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
                    respuesta = preguntar_a_qwen(pregunta, contexto)
                    print(f"\n[detector] LOBSTER DICE:\n{respuesta}\n")
                    guardar_respuesta(pregunta, respuesta)

            ultima_linea = len(lineas)

        time.sleep(5)

if __name__ == "__main__":
    iniciar()
