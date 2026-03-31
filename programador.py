import subprocess
import time
import os
from datetime import datetime

# ── Configuración ──────────────────────────────
HORA_ENTRADA    = "06:00"  # 6:00 AM Miami (lunes a viernes)
HORA_GRABACION  = "06:00"  # Empieza a grabar al entrar
EQUIPO          = "00 Loster Meetings"
CANAL           = "Lobster Meetings"
ZONA_HORARIA    = "America/New_York"
# ───────────────────────────────────────────────

def es_dia_semana():
    return datetime.now().weekday() < 5  # 0=lunes, 4=viernes

def hora_actual():
    return datetime.now().strftime("%H:%M")

def abrir_teams_canal():
    print(f"[programador] 🦞 Abriendo Teams en {EQUIPO} → {CANAL}...")
    subprocess.Popen(["open", "-a", "Microsoft Teams"])
    time.sleep(15)

    url = f"msteams://teams/channel?teamName={EQUIPO.replace(' ', '%20')}&channelName={CANAL.replace(' ', '%20')}"
    subprocess.Popen(["open", url])
    print(f"[programador] ✅ Teams abierto en {EQUIPO} → {CANAL}")

def iniciar_lobster():
    print("[programador] 🦞 Iniciando grabación...")
    os.system("python3 ~/lobster/grabador.py &")
    os.system("python3 ~/lobster/transcriptor.py &")
    os.system("python3 ~/lobster/detector.py &")
    os.system("python3 ~/lobster/resumidor.py &")
    os.system("python3 ~/lobster/ventana.py &")
    print("[programador] ✅ Todos los módulos activos")

def iniciar():
    print(f"[programador] 🦞 Esperando las {HORA_ENTRADA} de lunes a viernes...")
    ya_ejecutado = False

    while True:
        ahora = hora_actual()
        es_semana = es_dia_semana()

        if ahora == HORA_ENTRADA and es_semana and not ya_ejecutado:
            abrir_teams_canal()
            iniciar_lobster()
            ya_ejecutado = True
            print(f"[programador] ✅ Lobster activo para la reunión")

        if ahora == "00:00":
            ya_ejecutado = False

        time.sleep(30)

if __name__ == "__main__":
    iniciar()
