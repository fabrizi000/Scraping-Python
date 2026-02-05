# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from pathlib import Path
import threading

BASE_DIR = Path(__file__).resolve().parent / "scrapers"

SCRAPERS = {
    "Datos Macro": "datosmacro.py",
    "El País": "elpais.py",
    "Expansión": "expansion.py",
    "Vozpópuli": "vozpopuli.py",
}

INFO_TEXTS = {
    "Datos Macro": "DATOS MACRO\n\nObtiene indicadores macroeconómicos.\nSelecciona los paises mas influyentes en la economía.\nHace un resumen del porcentaje de paro de los paises selecionados.\nGenera varios CSV.",
    "El País": "NOTICIAS – EL PAÍS\n\nDescarga noticias económicas.\nDetecta todas las noticias disponibles.\nScrapea solo las compatibles con la estructura del scraper.",
    "Expansión": "NOTICIAS – EXPANSIÓN\n\nDescarga noticias económicas.\nDetecta todas las noticias disponibles.\nScrapea solo las compatibles con la estructura del scraper.",
    "Vozpópuli": "NOTICIAS – VOZPÓPULI\n\nDescarga artículos económicos\nDetecta todas los artículos disponibles.\nScrapea solo las compatibles con la estructura del scraper..",
}

def append_log(texto):
    log_text.configure(state="normal")
    log_text.insert("end", texto)
    log_text.see("end")
    log_text.configure(state="disabled")

def on_scraper_change(event=None):
    scraper = scraper_var.get()
    investing_frame.pack_forget()
    info_frame.pack_forget()

    if scraper == "Investing Economic Calendar":
        investing_frame.pack(fill="x", pady=10)
    else:
        info_text.set(INFO_TEXTS.get(scraper, ""))
        info_frame.pack(fill="x", pady=10)

def construir_comando():
    scraper = scraper_var.get()

    if scraper == "Investing Economic Calendar":
        fecha = fecha_var.get().strip()
        impacto = impacto_var.get()
        navegador = navegador_var.get()

        if not fecha:
            messagebox.showerror("Error", "Debes introducir una fecha.")
            return None

        script = "investing_chrome_selenium.py" if navegador == "chrome" else "investing_firefox_selenium.py"
        script_path = BASE_DIR / script

        return ["python3", str(script_path), "--fecha", fecha, "--impacto", impacto]

    else:
        script = SCRAPERS.get(scraper)
        if not script:
            messagebox.showerror("Error", "Scraper no reconocido")
            return None

        script_path = BASE_DIR / script
        return ["python3", str(script_path)]

def ejecutar_scraper():
    cmd = construir_comando()
    if not cmd:
        return

    if not Path(cmd[1]).exists():
        messagebox.showerror("Error", f"No se encuentra el script:\n{cmd[1]}")
        return

    log_text.configure(state="normal")
    log_text.delete("1.0", "end")
    log_text.configure(state="disabled")

    append_log(f"Iniciando: {' '.join(cmd)}\n\n")

    def run():
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for linea in proc.stdout:
                root.after(0, append_log, linea)
            root.after(0, append_log, "\n--- Proceso finalizado ---\n")
        except Exception as e:
            root.after(0, append_log, f"\nError: {e}\n")

    threading.Thread(target=run, daemon=True).start()

# -------- GUI --------

root = tk.Tk()
root.title("WEBBUSTER")
root.geometry("540x560")

frame = ttk.Frame(root, padding=15)
frame.pack(fill="both", expand=True)

ttk.Label(frame, text="Selecciona el scraper:", font=("Arial", 11, "bold")).pack(anchor="w")

scraper_var = tk.StringVar(value="Investing Economic Calendar")
scraper_combo = ttk.Combobox(
    frame,
    textvariable=scraper_var,
    values=["Investing Economic Calendar"] + list(SCRAPERS.keys()),
    state="readonly"
)
scraper_combo.pack(fill="x")
scraper_combo.bind("<<ComboboxSelected>>", on_scraper_change)

content_frame = ttk.Frame(frame)
content_frame.pack(fill="x")

investing_frame = ttk.LabelFrame(content_frame, text="Opciones Investing")

ttk.Label(investing_frame, text="Fecha (YYYY-MM-DD por ejemplo: 2024-2-15, 2024-12-15, 2024-2-5):").pack(anchor="w")
fecha_var = tk.StringVar()
ttk.Entry(investing_frame, textvariable=fecha_var).pack(fill="x")

ttk.Label(investing_frame, text="Impacto:").pack(anchor="w")
impacto_var = tk.StringVar(value="3")
ttk.Combobox(investing_frame, textvariable=impacto_var, values=["1", "2", "3"], state="readonly").pack(fill="x")

ttk.Label(investing_frame, text="Navegador:").pack(anchor="w")
navegador_var = tk.StringVar(value="firefox")
ttk.Combobox(investing_frame, textvariable=navegador_var, values=["firefox", "chrome"], state="readonly").pack(fill="x")

info_frame = ttk.LabelFrame(content_frame, text="Información del scraper")
info_text = tk.StringVar()
ttk.Label(info_frame, textvariable=info_text, justify="left", wraplength=500).pack(anchor="w", padx=10, pady=10)

ttk.Button(frame, text="Iniciar Scraping", command=ejecutar_scraper).pack(pady=10)

log_frame = ttk.LabelFrame(frame, text="Salida del proceso")
log_text = tk.Text(log_frame, height=10, state="disabled")
log_text.pack(fill="both", expand=True, padx=5, pady=5)
log_frame.pack(fill="both", expand=True, pady=10)

on_scraper_change()
root.mainloop()