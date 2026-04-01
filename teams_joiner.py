import pyautogui
import subprocess
import time
import os
from datetime import datetime

# ── Configuración ──────────────────────────────
HORA_INICIO     = "13:38"  # 7:00 AM Miami
HORA_FIN        = "18:00"  # Deja de intentar
EQUIPO          = "00 Loster Meetings"
CANAL           = "Lobster Meetings"
BOTON_JOIN      = os.path.expanduser("~/lobster/boton_join.png")
CONFIANZA       = 0.8      # 80% de similitud para detectar el botón
# ───────────────────────────────────────────────

def es_dia_semana():
    return True

def hora_actual_int():
    now = datetime.now()
    return now.hour * 60 + now.minute

def hora_a_minutos(hora_str):
    h, m = map(int, hora_str.split(":"))
    return h * 60 + m

def abrir_teams_canal():
    print(f"[joiner] 🦞 Abriendo Teams en {EQUIPO} → {CANAL}...")
    subprocess.Popen(["open", "-a", "Microsoft Teams"])
    time.sleep(15)
    url = f"https://teams.microsoft.com/l/channel/general?teamName={EQUIPO.replace(chr(32), chr(37)+chr(50)+chr(48))}&channelName={CANAL.replace(chr(32), chr(37)+chr(50)+chr(48))}"
    subprocess.Popen(["open", "-a", "Microsoft Teams", url])
    time.sleep(5)

def buscar_y_unirse():
    print("[joiner] 🦞 Buscando botón Join en pantalla...")
    try:
        ubicacion = pyautogui.locateOnScreen(BOTON_JOIN, confidence=CONFIANZA)
        if ubicacion:
            print(f"[joiner] ✅ Botón Join encontrado en {ubicacion}")
            centro = pyautogui.center(ubicacion)
            pyautogui.click(centro)
            print("[joiner] ✅ Clic en Join realizado")
            time.sleep(5)

            # Buscar botón de Request to Join si hay lobby
            print("[joiner] 🦞 Verificando lobby...")
            pyautogui.click(centro)
            return True
        else:
            print("[joiner] ❌ Botón Join no encontrado, reintentando en 1 hora...")
            return False
    except Exception as e:
        print(f"[joiner] ❌ Error: {e}")
        return False

def desactivar_mic_camara():
    print("[joiner] 🔇 Desactivando micrófono y cámara...")
    time.sleep(3)
    pyautogui.hotkey('command', 'shift', 'm')  # Mute mic
    time.sleep(1)
    pyautogui.hotkey('command', 'shift', 'o')  # Apagar cámara
    print("[joiner] ✅ Mic y cámara desactivados")


def iniciar_lobster():
    print("[joiner] 🦞 Iniciando módulos de grabación...")
    os.system("python3 ~/lobster/grabador.py &")
    os.system("python3 ~/lobster/transcriptor.py &")
    os.system("python3 ~/lobster/detector.py &")
    os.system("python3 ~/lobster/resumidor.py &")
    print("[joiner] ✅ Todos los módulos activos")

def iniciar():
    print(f"[joiner] 🦞 Esperando las {HORA_INICIO} de lunes a viernes...")
    unido = False
    ultimo_intento = None

    while True:
        ahora = hora_actual_int()
        inicio = hora_a_minutos(HORA_INICIO)
        fin = hora_a_minutos(HORA_FIN)
        es_semana = es_dia_semana()

        if es_semana and inicio <= ahora <= fin and not unido:
            if ultimo_intento is None or (ahora - ultimo_intento) >= 60:
                abrir_teams_canal()
                if buscar_y_unirse():
                    desactivar_mic_camara()
                    iniciar_lobster()
                    unido = True
                    print("[joiner] 🦞 ¡Lobster en la reunión!")
                else:
                    ultimo_intento = ahora

        if ahora < inicio:
            unido = False
            ultimo_intento = None

        time.sleep(30)

if __name__ == "__main__":
    iniciar()
