import subprocess
import time
import os
from datetime import datetime
from config import (
    HORA_INICIO, HORA_FIN, EQUIPO, CANAL, BASE_DIR
)
from logger import get_logger

# ── Setup ───────────────────────────────────────
log = get_logger("joiner")
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
        log.warning(f"AppleScript error: {resultado.stderr.strip()}")
        return False, resultado.stderr.strip()
    return True, resultado.stdout.strip()

def abrir_teams():
    log.info("🦞 Abriendo Microsoft Teams...")
    script = '''
    tell application "Microsoft Teams"
        activate
    end tell
    '''
    correr_applescript(script)
    time.sleep(15)
    log.info("Teams abierto")

def buscar_y_unirse():
    log.info("🦞 Buscando botón Join con AppleScript...")

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
            log.info(f"Botón '{texto_boton}' encontrado y clickeado")
            return True

    # Estrategia 2: búsqueda parcial por "join"
    script = '''
    tell application "System Events"
        tell process "Microsoft Teams"
            set todos_botones to every button of window 1
            repeat with btn in todos_botones
                set nombre_btn to name of btn
                if nombre_btn contains "join" or nombre_btn contains "Join" then
                    click btn
                    return nombre_btn
                end if
            end repeat
            return "not_found"
        end tell
    end tell
    '''
    exito, output = correr_applescript(script)
    if exito and output != "not_found" and output != "":
        log.info(f"Botón encontrado por búsqueda parcial: '{output}'")
        return True

    log.error("Botón Join no encontrado")
    return False

def manejar_permisos_sistema():
    log.info("Verificando diálogos de permisos del sistema...")
    time.sleep(3)

    script = '''
    tell application "System Events"
        if exists (process "UserNotificationCenter") then
            tell process "UserNotificationCenter"
                try
                    click button "OK" of window 1
                    return "accepted_ok"
                end try
                try
                    click button "Allow" of window 1
                    return "accepted_allow"
                end try
            end tell
        end if
        return "no_dialog"
    end tell
    '''
    exito, output = correr_applescript(script)
    if output in ("accepted_ok", "accepted_allow"):
        log.info(f"Permiso aceptado ({output})")
        time.sleep(2)
        correr_applescript(script)
    else:
        log.info("Sin diálogos de permisos pendientes")

def desactivar_mic_camara():
    log.info("Desactivando micrófono y cámara...")
    time.sleep(3)

    script = '''
    tell application "System Events"
        tell process "Microsoft Teams"
            key code 46 using {command down, shift down}
        end tell
    end tell
    '''
    correr_applescript(script)
    time.sleep(1)

    script = '''
    tell application "System Events"
        tell process "Microsoft Teams"
            key code 31 using {command down, shift down}
        end tell
    end tell
    '''
    correr_applescript(script)
    log.info("Mic y cámara desactivados")

def iniciar_lobster():
    log.info("🦞 Iniciando módulos de grabación...")
    modulos = ["grabador.py", "transcriptor.py", "detector.py", "resumidor.py"]
    for modulo in modulos:
        os.system(f"python3 {BASE_DIR}/{modulo} &")
    log.info("Todos los módulos activos")

def iniciar():
    log.info(f"🦞 Esperando las {HORA_INICIO} de lunes a viernes...")
    unido = False
    ultimo_intento = None

    while True:
        ahora = hora_actual_int()
        inicio = hora_a_minutos(HORA_INICIO)
        fin = hora_a_minutos(HORA_FIN)

        if es_dia_semana() and inicio <= ahora <= fin and not unido:
            if ultimo_intento is None or (ahora - ultimo_intento) >= 60:
                abrir_teams()
                if buscar_y_unirse():
                    time.sleep(3)
                    manejar_permisos_sistema()
                    desactivar_mic_camara()
                    iniciar_lobster()
                    unido = True
                    log.info("🦞 ¡Lobster en la reunión!")
                else:
                    ultimo_intento = ahora
                    log.warning("Botón Join no encontrado, reintentando en 1 hora...")

        if ahora < inicio:
            unido = False
            ultimo_intento = None

        time.sleep(30)

if __name__ == "__main__":
    iniciar()