import subprocess
import time
import os
from datetime import datetime

# ── Configuración ──────────────────────────────
HORA_INICIO  = "13:38"
HORA_FIN     = "18:00"
EQUIPO       = "00 Loster Meetings"
CANAL        = "Lobster Meetings"
# ───────────────────────────────────────────────

def hora_actual_int():
    now = datetime.now()
    return now.hour * 60 + now.minute

def hora_a_minutos(hora_str):
    h, m = map(int, hora_str.split(":"))
    return h * 60 + m

def es_dia_semana():
    return datetime.now().weekday() < 5

def correr_applescript(script):
    resultado = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True
    )
    if resultado.returncode != 0:
        print(f"[joiner] ⚠️ AppleScript error: {resultado.stderr.strip()}")
        return False, resultado.stderr.strip()
    return True, resultado.stdout.strip()

def abrir_teams():
    print("[joiner] 🦞 Abriendo Microsoft Teams...")
    script = '''
    tell application "Microsoft Teams"
        activate
    end tell
    '''
    correr_applescript(script)
    time.sleep(15)
    print("[joiner] ✅ Teams abierto")

def buscar_y_unirse():
    print("[joiner] 🦞 Buscando botón Join con AppleScript...")

    # Estrategia 1: buscar por nombre exacto
    for texto_boton in ["Join", "Join now", "Ask to join"]:
        script = f'''
        tell application "System Events"
            tell process "Microsoft Teams"
                set btn to first button whose name is "{texto_boton}"
                click btn
                return "clicked"
            end tell
        end tell
        '''
        exito, output = correr_applescript(script)
        if exito and output == "clicked":
            print(f"[joiner] ✅ Botón '{texto_boton}' encontrado y clickeado")
            return True

    # Estrategia 2: búsqueda parcial