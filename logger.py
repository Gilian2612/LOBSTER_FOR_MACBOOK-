import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOG_FILE

# ── Configuración ──────────────────────────────
NIVEL        = logging.DEBUG
MAX_BYTES    = 5 * 1024 * 1024  # 5MB por archivo de log
BACKUPS      = 3                # mantiene los últimos 3 archivos
# ───────────────────────────────────────────────

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def get_logger(nombre):
    """
    Devuelve un logger con el nombre del módulo.
    Uso en cada módulo:
        from logger import get_logger
        log = get_logger("grabador")
        log.info("Iniciando...")
        log.error("Algo falló")
    """
    logger = logging.getLogger(nombre)

    # evitar duplicar handlers si get_logger se llama más de una vez
    if logger.handlers:
        return logger

    logger.setLevel(NIVEL)

    # ── Formato ────────────────────────────────
    # [10:32:15] [grabador] INFO — Mensaje aquí
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(name)s] %(levelname)s — %(message)s",
        datefmt="%H:%M:%S"
    )

    # ── Handler 1: archivo rotativo ────────────
    # cuando el log llega a 5MB crea uno nuevo
    # y guarda hasta 3 archivos anteriores
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUPS,
        encoding="utf-8"
    )
    file_handler.setLevel(NIVEL)
    file_handler.setFormatter(formatter)

    # ── Handler 2: consola ─────────────────────
    # sigue imprimiendo en terminal para desarrollo
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger