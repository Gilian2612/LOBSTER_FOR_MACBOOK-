# 🦞 Hey Lobster

Asistente de reuniones autónomo para Mac. Entra solo a Teams, graba, transcribe, responde comandos de voz y genera resúmenes automáticos. (EXPERIMENTAL)
Diseño sigue en proceso

---

## Estructura del proyecto
```
lobster/
├── config.py          # Configuración centralizada (rutas, horarios, modelos)
├── logger.py          # Logger compartido con rotación de archivo
├── iniciar.py         # Orquestador principal — lanza y supervisa todos los módulos
├── teams_joiner.py    # Entra automáticamente a la reunión de Teams
├── grabador.py        # Captura audio desde BlackHole 2ch
├── transcriptor.py    # Transcribe audio con Whisper
├── detector.py        # Detecta "Hey Lobster" y responde preguntas
├── resumidor.py       # Genera resúmenes cada 30 min y al cierre del día
└── ventana.py         # Ventana flotante con Respuestas, Transcript y Logs
```

---

## Requisitos en la Mac

- Python 3.x
- BlackHole 2ch instalado como dispositivo de audio virtual
- Microsoft Teams instalado
- Ollama corriendo con el modelo `qwen2.5-coder:14b`
- Permisos de Accesibilidad para Terminal y Python en:
  `System Preferences → Privacy & Security → Accessibility`

### Instalar dependencias
```bash
pip3 install whisper sounddevice soundfile numpy requests
```

---

## Cómo correr
```bash
cd ~/lobster
python3 iniciar.py
```

---

## Configuración

Todo está centralizado en `config.py`. Los valores que más vas a necesitar cambiar:

| Variable | Descripción | Default |
|---|---|---|
| `HORA_INICIO` | Hora de entrada a la reunión | `"13:38"` |
| `HORA_FIN` | Hora de fin del día | `"18:00"` |
| `EQUIPO` | Nombre del equipo en Teams | `"00 Loster Meetings"` |
| `CANAL` | Nombre del canal | `"Lobster Meetings"` |
| `DEVICE_INDEX` | Índice de BlackHole en sounddevice | `4` |
| `MODELO_WHISPER` | Modelo de Whisper | `"small"` |
| `MODELO_OLLAMA` | Modelo de Ollama | `"qwen2.5-coder:14b"` |
| `UMBRAL_SILENCIO` | RMS mínimo para transcribir | `0.01` |

---

## Historial de cambios

### Sesión 1 — Refactor v1 → v2

#### Fase 1 — Bugs críticos
- **transcriptor.py** — filtro de silencio por RMS antes de llamar a Whisper + supresión de tokens de alucinación (`"You"`, `"Thank you"`, etc.)
- **grabador.py** — corregido `CHANNELS = 3` → `CHANNELS = 1` (BlackHole 2ch es mono/stereo, no 3 canales)
- **teams_joiner.py** — reemplazado PyAutoGUI (fallaba en pantallas Retina) por AppleScript + Accessibility API para click robusto en botón Join
- **teams_joiner.py** — manejo de diálogos de permisos de mic/cámara de macOS con `osascript`

#### Fase 2 — Arquitectura
- **config.py** *(nuevo)* — todas las rutas, horarios y parámetros centralizados en un solo archivo
- **logger.py** *(nuevo)* — logger compartido con rotación de archivo (5MB, 3 backups) y colores por nivel
- **iniciar.py** — reescrito como orquestador real con `subprocess.Popen`, supervisión de procesos y cierre limpio con `Ctrl+C`
- Todos los módulos actualizados para importar desde `config.py` y usar `logger.py`

#### Fase 3 — Robustez
- **detector.py** — timeout y manejo de errores en llamadas a Ollama
- **resumidor.py** — timeout y manejo de errores en llamadas a Ollama
- **grabador.py** — reconexión automática si BlackHole se desconecta
- **resumidor.py** — resumen final del día al llegar a `HORA_FIN` con análisis de tareas automatizables

#### Fase 4 — UI
- **ventana.py** — tercera pestaña de Logs en vivo con colores por nivel (ERROR=rojo, WARNING=amarillo, DEBUG=gris)

---

## Roadmap pendiente

- [ ] Probar AppleScript en reunión real de Teams y ajustar si el botón Join tiene nombre diferente
- [ ] Calibrar `UMBRAL_SILENCIO` según el ambiente de grabación
- [ ] Verificar `DEVICE_INDEX` de BlackHole después de cada reinicio de la Mac
- [ ] Unificar `programador.py` con `teams_joiner.py` (pendiente de siguiente sesión)






REFACTOR SOLICITUD - REQUERIMIENTO:
- Permitir que el Lobster se pueda unir a la reunion (invitado por un miemrbo del equipo)

