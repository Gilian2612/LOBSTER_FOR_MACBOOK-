import subprocess
import time
import os
import signal
from logger import get_logger
from config import BASE_DIR

# ── Setup ───────────────────────────────────────
log = get_logger("iniciar")
# ───────────────────────────────────────────────

# Módulos que se lanzan y supervisan automáticamente
# si alguno cae, el orquestador lo relanza
MODULOS = [
    ("ollama",       ["ollama", "serve"]),
    ("joiner",       ["python3", f"{BASE_DIR}/teams_joiner.py"]),
    ("grabador",     ["python3", f"{BASE_DIR}/grabador.py"]),
    ("transcriptor", ["python3", f"{BASE_DIR}/transcriptor.py"]),
    ("detector",     ["python3", f"{BASE_DIR}/detector.py"]),
    ("resumidor",    ["python3", f"{BASE_DIR}/resumidor.py"]),
]

procesos = {}  # nombre → subprocess.Popen

def lanzar_modulo(nombre, comando):
    """Lanza un módulo y registra el proceso."""
    log.info(f"Arrancando {nombre}...")
    try:
        p = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        procesos[nombre] = p
        log.info(f"{nombre} iniciado con PID {p.pid}")
        return p
    except FileNotFoundError:
        log.error(f"No se encontró el comando para {nombre}: {comando}")
        return None

def detener_todo():
    """Detiene todos los módulos limpiamente."""
    log.info("Deteniendo todos los módulos...")
    for nombre, p in procesos.items():
        if p and p.poll() is None:  # sigue corriendo
            log.info(f"Deteniendo {nombre} (PID {p.pid})...")
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                log.warning(f"{nombre} no terminó, forzando...")
                p.kill()
    log.info("Todos los módulos detenidos.")

def supervisar():
    """
    Loop principal — revisa cada 30 segundos si algún
    módulo cayó y lo relanza automáticamente.
    """
    while True:
        time.sleep(30)
        for nombre, comando in MODULOS:
            p = procesos.get(nombre)
            if p is None:
                continue
            if p.poll() is not None:
                # el proceso terminó inesperadamente
                codigo = p.returncode
                log.warning(f"{nombre} cayó con código {codigo}, relanzando...")
                lanzar_modulo(nombre, comando)

def iniciar():
    log.info("🦞 Iniciando Hey Lobster...")

    # lanzar todos los módulos
    for nombre, comando in MODULOS:
        lanzar_modulo(nombre)
        time.sleep(2)  # pequeña pausa entre módulos

    log.info("🦞 Todos los módulos activos. Abriendo ventana...")

    # manejar Ctrl+C para cierre limpio
    def handle_sigint(sig, frame):
        log.info("Señal de cierre recibida...")
        detener_todo()
        exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    # lanzar ventana en hilo principal
    # (bloqueante, se cierra cuando el usuario cierra la ventana)
    try:
        os.system(f"python3 {BASE_DIR}/ventana.py")
    except Exception as e:
        log.error(f"Error en ventana: {e}")

    # si la ventana se cierra, supervisar módulos
    supervisar()

if __name__ == "__main__":
    iniciar()