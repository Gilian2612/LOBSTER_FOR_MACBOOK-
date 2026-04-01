import os

# ── Rutas base ─────────────────────────────────
BASE_DIR        = os.path.expanduser("~/lobster")
AUDIO_DIR       = os.path.join(BASE_DIR, "audio_chunks")
TRANSCRIPT_FILE = os.path.join(BASE_DIR, "transcript.txt")
RESPUESTAS_FILE = os.path.join(BASE_DIR, "respuestas.txt")
LOG_FILE        = os.path.join(BASE_DIR, "lobster.log")

# ── Teams ───────────────────────────────────────
EQUIPO       = "00 Loster Meetings"
CANAL        = "Lobster Meetings"
HORA_INICIO  = "13:38"
HORA_FIN     = "18:00"

# ── Audio ───────────────────────────────────────
DEVICE_INDEX   = 4        # BlackHole 2ch
SAMPLE_RATE    = 16000
CHANNELS       = 1
CHUNK_SEGUNDOS = 30

# ── Whisper ─────────────────────────────────────
MODELO_WHISPER   = "small"
IDIOMA           = None
UMBRAL_SILENCIO  = 0.01
UMBRAL_NO_SPEECH = 0.6

# ── Ollama ──────────────────────────────────────
OLLAMA_URL      = "http://localhost:11434/api/generate"
MODELO_OLLAMA   = "qwen2.5-coder:14b"
CONTEXTO_LINEAS = 50
OLLAMA_TIMEOUT  = 30

# ── Resumidor ───────────────────────────────────
INTERVALO_RESUMEN = 1800  # 30 minutos

# ── Detector ────────────────────────────────────
PALABRA_CLAVE = "hey lobster"

# ── UI ──────────────────────────────────────────
INTERVALO_REFRESCO = 3    # segundos