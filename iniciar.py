import subprocess
import os

LOBSTER_DIR = os.path.expanduser("~/lobster")

modulos = [
    ("ollama",       ["ollama", "serve"]),
    ("teams_joiner", ["python3", f"{LOBSTER_DIR}/teams_joiner.py"]),
]

procesos = []

print("🦞 Iniciando Hey Lobster...")

for nombre, comando in modulos:
    print(f"  ▶ Arrancando {nombre}...")
    p = subprocess.Popen(comando,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    procesos.append((nombre, p))

print("🦞 Todos los módulos activos. Abriendo ventana...\n")

try:
    os.system(f"python3 {LOBSTER_DIR}/ventana.py")
except KeyboardInterrupt:
    print("\n🦞 Deteniendo Hey Lobster...")
    for nombre, p in procesos:
        print(f"  ■ Deteniendo {nombre}...")
        p.terminate()
    print("🦞 See you later!")
