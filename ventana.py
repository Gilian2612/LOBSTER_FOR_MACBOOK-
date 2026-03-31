import tkinter as tk
import os
import time
import threading
from datetime import datetime

# ── Configuración ──────────────────────────────
RESPUESTAS_FILE = os.path.expanduser("~/lobster/respuestas.txt")
TRANSCRIPT_FILE = os.path.expanduser("~/lobster/transcript.txt")
INTERVALO_REFRESCO = 3  # segundos
# ───────────────────────────────────────────────

class VentanaLobster:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🦞 Hey Lobster")
        self.root.geometry("400x600")
        self.root.attributes("-topmost", True)  # Siempre visible
        self.root.configure(bg="#1e1e2e")

        # Título
        titulo = tk.Label(self.root, text="🦞 Hey Lobster",
                         bg="#1e1e2e", fg="#cdd6f4",
                         font=("Helvetica", 16, "bold"))
        titulo.pack(pady=10)

        # Pestañas
        self.frame_botones = tk.Frame(self.root, bg="#1e1e2e")
        self.frame_botones.pack(fill="x", padx=10)

        self.btn_respuestas = tk.Button(self.frame_botones,
                                        text="Respuestas",
                                        command=self.mostrar_respuestas,
                                        bg="#89b4fa", fg="#1e1e2e",
                                        font=("Helvetica", 10, "bold"),
                                        relief="flat", padx=10)
        self.btn_respuestas.pack(side="left", padx=5, pady=5)

        self.btn_transcript = tk.Button(self.frame_botones,
                                        text="Transcript",
                                        command=self.mostrar_transcript,
                                        bg="#313244", fg="#cdd6f4",
                                        font=("Helvetica", 10),
                                        relief="flat", padx=10)
        self.btn_transcript.pack(side="left", padx=5, pady=5)

        # Área de texto
        self.texto = tk.Text(self.root, bg="#313244", fg="#cdd6f4",
                            font=("Helvetica", 11),
                            wrap="word", relief="flat",
                            padx=10, pady=10)
        self.texto.pack(fill="both", expand=True, padx=10, pady=10)

        # Estado
        self.estado = tk.Label(self.root, text="● En vivo",
                              bg="#1e1e2e", fg="#a6e3a1",
                              font=("Helvetica", 9))
        self.estado.pack(pady=5)

        self.modo = "respuestas"
        self.ultima_linea = 0

        # Hilo de actualización
        self.hilo = threading.Thread(target=self.actualizar_loop, daemon=True)
        self.hilo.start()

    def mostrar_respuestas(self):
        self.modo = "respuestas"
        self.btn_respuestas.configure(bg="#89b4fa", fg="#1e1e2e")
        self.btn_transcript.configure(bg="#313244", fg="#cdd6f4")
        self.refrescar()

    def mostrar_transcript(self):
        self.modo = "transcript"
        self.btn_transcript.configure(bg="#89b4fa", fg="#1e1e2e")
        self.btn_respuestas.configure(bg="#313244", fg="#cdd6f4")
        self.refrescar()

    def leer_archivo(self, archivo):
        if not os.path.exists(archivo):
            return "Sin contenido aún..."
        with open(archivo, "r", encoding="utf-8") as f:
            return f.read()

    def refrescar(self):
        archivo = RESPUESTAS_FILE if self.modo == "respuestas" else TRANSCRIPT_FILE
        contenido = self.leer_archivo(archivo)
        self.texto.delete("1.0", tk.END)
        self.texto.insert(tk.END, contenido)
        self.texto.see(tk.END)  # Auto-scroll al final

    def actualizar_loop(self):
        while True:
            self.refrescar()
            time.sleep(INTERVALO_REFRESCO)

    def iniciar(self):
        print("[ventana] 🦞 Ventana flotante iniciada")
        self.root.mainloop()

if __name__ == "__main__":
    VentanaLobster().iniciar()
