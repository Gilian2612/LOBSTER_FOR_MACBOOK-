import os
import time
import requests
from datetime import datetime

# ── Configuración ──────────────────────────────
TRANSCRIPT_FILE = os.path.expanduser("~/lobster/transcript.txt")
RESPUESTAS_FILE = os.path.expanduser("~/lobster/respuestas.txt")
OLLAMA_URL      = "http://localhost:11434/api/generate"
MODELO          = "qwen2.5-coder:14b"
INTERVALO       = 1800  # 30 minutos en segundos
# ───────────────────────────────────────────────

def obtener_transcript():
    if not os.path.exists(TRANSCRIPT_FILE):
        return ""
    with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def generar_resumen(contexto):
    prompt = f"""Eres un asistente de reuniones llamado Lobster.
Aqui esta la transcripcion completa de la reunion hasta ahora:

{contexto}

Genera un resumen ejecutivo con:
1. Temas principales discutidos
2. Decisiones tomadas
3. Proximos pasos o action items

Se conciso y claro. Responde en el idioma predominante de la transcripcion."""

    print(f"[resumidor] 🦞 Generando resumen...")
    response = requests.post(OLLAMA_URL, json={
        "model": MODELO,
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"]

def guardar_resumen(resumen):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(RESPUESTAS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"[{timestamp}] RESUMEN AUTOMATICO\n")
        f.write(f"{'='*50}\n")
        f.write(f"{resumen}\n")
        f.write(f"{'='*50}\n")
    print(f"[resumidor] ✅ Resumen guardado en respuestas.txt")

def iniciar():
    print(f"[resumidor] 🦞 Resumen automatico cada 30 minutos...")
    while True:
        time.sleep(INTERVALO)
        contexto = obtener_transcript()
        if contexto.strip():
            resumen = generar_resumen(contexto)
            print(f"\n[resumidor] RESUMEN:\n{resumen}\n")
            guardar_resumen(resumen)
        else:
            print("[resumidor] Sin transcript aun, esperando...")

if __name__ == "__main__":
    iniciar()
