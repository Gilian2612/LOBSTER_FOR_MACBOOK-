import tkinter as tk
import os
import time
import threading
from config import RESPUESTAS_FILE, TRANSCRIPT_FILE, LOG_FILE, INTERVALO_REFRESCO
from logger import get_logger

# ── Setup ───────────────────────────────────────
log = get_logger("ventana")
# ───────────────────────────────────────────────

PESTANAS = {
    "respuestas": RESPUESTAS_FILE,
    "transcript": TRANSCRIPT_FILE,
    "logs":       LOG_FILE,
}

COLORES = {
    "bg":        "#1e1e2e",
    "surface":   "#313244",
    "texto":     "#cdd6f4",
    "azul":      "#89b4fa",
    "verde":     "#a6e3a1",
    "amarillo":  "#f9e2af",
    "rojo":      "#f38ba8",
    "gris":      "#6c7086",
}

class VentanaLobster:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🦞 Hey Lobster")
        self.root.geometry("420x650")
        self.root.attributes("-topmost", True)
        self.root.configure(bg=COLORES["bg"])

        self._construir_ui()

        self.modo = "respuestas"
        self.hilo = threading.Thread(target=self._loop_refresco, daemon=True)
        self.hilo.start()

    def _construir_ui(self):
        # ── Título ─────────────────────────────
        tk.Label(
            self.root, text="🦞 Hey Lobster",
            bg=COLORES["bg"], fg=COLORES["texto"],
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)

        # ── Pestañas ───────────────────────────
        self.frame_tabs = tk.Frame(self.root, bg=COLORES["bg"])
        self.frame_tabs.pack(fill="x", padx=10)

        self.botones = {}
        tabs = [
            ("respuestas", "Respuestas"),
            ("transcript", "Transcript"),
            ("logs",       "Logs"),
        ]
        for modo, label in tabs:
            btn = tk.Button(
                self.frame_tabs,
                text=label,
                command=lambda m=modo: self._cambiar_tab(m),
                bg=COLORES["surface"], fg=COLORES["texto"],
                font=("Helvetica", 10),
                relief="flat", padx=10
            )
            btn.pack(side="left", padx=4, pady=5)
            self.botones[modo] = btn

        # ── Área de texto ──────────────────────
        self.texto = tk.Text(
            self.root,
            bg=COLORES["surface"], fg=COLORES["texto"],
            font=("Helvetica", 11),
            wrap="word", relief="flat",
            padx=10, pady=10
        )
        self.texto.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # colores para niveles de log
        self.texto.tag_config("ERROR",   foreground=COLORES["rojo"])
        self.texto.tag_config("WARNING", foreground=COLORES["amarillo"])
        self.texto.tag_config("INFO",    foreground=COLORES["texto"])
        self.texto.tag_config("DEBUG",   foreground=COLORES["gris"])

        # ── Barra de estado ────────────────────
        self.estado = tk.Label(
            self.root, text="● En vivo",
            bg=COLORES["bg"], fg=COLORES["verde"],
            font=("Helvetica", 9)
        )
        self.estado.pack(pady=5)

        # activar tab inicial
        self._cambiar_tab("respuestas")

    def _cambiar_tab(self, modo):
        self.modo = modo
        for m, btn in self.botones.items():
            if m == modo:
                btn.configure(bg=COLORES["azul"], fg=COLORES["bg"])
            else:
                btn.configure(bg=COLORES["surface"], fg=COLORES["texto"])
        self._refrescar()

    def _leer_archivo(self, archivo):
        if not os.path.exists(archivo):
            return [("INFO", "Sin contenido aún...")]
        with open(archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()

        # si es el log, colorear por nivel
        if archivo == LOG_FILE:
            resultado = []
            for linea in lineas[-200:]:  # últimas 200 líneas
                if "ERROR" in linea:
                    resultado.append(("ERROR", linea))
                elif "WARNING" in linea:
                    resultado.append(("WARNING", linea))
                elif "DEBUG" in linea:
                    resultado.append(("DEBUG", linea))
                else:
                    resultado.append(("INFO", linea))
            return resultado

        # para transcript y respuestas devolver texto plano
        return [("INFO", "".join(lineas))]

    def _refrescar(self):
        archivo = PESTANAS[self.modo]
        contenido = self._leer_archivo(archivo)

        self.texto.configure(state="normal")
        self.texto.delete("1.0", tk.END)

        for nivel, linea in contenido:
            self.texto.insert(tk.END, linea, nivel)

        self.texto.configure(state="disabled")
        self.texto.see(tk.END)

    def _loop_refresco(self):
        while True:
            try:
                self.root.after(0, self._refrescar)
            except Exception as e:
                log.error(f"Error refrescando ventana: {e}")
            time.sleep(INTERVALO_REFRESCO)

    def iniciar(self):
        log.info("🦞 Ventana flotante iniciada")
        self.root.mainloop()

if __name__ == "__main__":
    VentanaLobster().iniciar()