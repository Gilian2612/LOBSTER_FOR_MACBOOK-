import os
import time
import requests
from datetime import datetime
from config import (
    TRANSCRIPT_FILE, RESPUESTAS_FILE, OLLAMA_URL,
    MODELO_OLLAMA, INTERVALO_RESUMEN, OLLAMA_TIMEOUT,
    HORA_FIN
)
from logger import get_logger

# ── Setup ───────────────────────────────────────
log = get_logger("resumidor")
# ───────────────────────────────────────────────

def obtener_transcript():
    if not os.path.exists(TRANSCRIPT_FILE):
        return ""
    with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def generar_resumen(contexto, prompt_extra=""):
    prompt = f"""Eres un asistente de reuniones llamado Lobster.
Aqui esta la transcripcion completa de la reunion hasta ahora:

{contexto}

{prompt_extra}

Responde en el idioma predominante de la transcripcion."""

    log.info("Generando resumen con Ollama...")
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
        return None
    except requests.ConnectionError:
        log.error("No se pudo conectar a Ollama — ¿está corriendo?")
        return None
    except Exception as e:
        log.error(f"Error inesperado consultando Ollama: {e}")
        return None

def guardar_resumen(resumen, titulo="RESUMEN AUTOMATICO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(RESPUESTAS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"[{timestamp}] {titulo}\n")
        f.write(f"{'='*50}\n")
        f.write(f"{resumen}\n")
        f.write(f"{'='*50}\n")
    log.info(f"{titulo} guardado en respuestas.txt")

def resumen_periodico():
    """Genera resumen ejecutivo cada 30 minutos."""
    prompt_extra = """Genera un resumen ejecutivo con:
1. Temas principales discutidos
2. Decisiones tomadas
3. Proximos pasos o action items

Se conciso y claro."""
    contexto = obtener_transcript()
    if not contexto.strip():
        log.info("Sin transcript aún, esperando...")
        return
    resumen = generar_resumen(contexto, prompt_extra)
    if resumen:
        log.info(f"RESUMEN:\n{resumen}")
        guardar_resumen(resumen, "RESUMEN AUTOMATICO")

def resumen_final_del_dia():
    """
    Se ejecuta al final del horario laboral.
    Analiza el transcript completo y sugiere qué se puede automatizar.
    """
    log.info("🦞 Generando resumen final del día...")
    contexto = obtener_transcript()
    if not contexto.strip():
        log.info("Sin transcript para resumen final.")
        return

    prompt_extra = """Genera un reporte de fin de dia con estas secciones:

1. RESUMEN EJECUTIVO DEL DIA
   - Temas principales tratados
   - Decisiones importantes tomadas

2. ACTION ITEMS
   - Lista de tareas pendientes mencionadas
   - Responsables si se mencionaron

3. OPORTUNIDADES DE AUTOMATIZACION
   - Tareas repetitivas detectadas en la reunion
   - Procesos manuales que podrían automatizarse
   - Sugerencias concretas de cómo automatizarlos

Se detallado en la sección de automatizaciones."""

    resumen = generar_resumen(contexto, prompt_extra)
    if resumen:
        log.info(f"RESUMEN FINAL:\n{resumen}")
        guardar_resumen(resumen, "RESUMEN FINAL DEL DIA")

def hora_actual_int():
    now = datetime.now()
    return now.hour * 60 + now.minute

def hora_a_minutos(hora_str):
    h, m = map(int, hora_str.split(":"))
    return h * 60 + m

def iniciar():
    log.info("🦞 Resumen automático cada 30 minutos...")
    resumen_final_ejecutado = False

    while True:
        time.sleep(INTERVALO_RESUMEN)

        ahora = hora_actual_int()
        fin = hora_a_minutos(HORA_FIN)

        # resumen periódico cada 30 minutos
        resumen_periodico()

        # resumen final al llegar a HORA_FIN
        if ahora >= fin and not resumen_final_ejecutado:
            resumen_final_del_dia()
            resumen_final_ejecutado = True

        # resetear para el día siguiente
        if ahora < hora_a_minutos("06:00"):
            resumen_final_ejecutado = False

if __name__ == "__main__":
    iniciar()