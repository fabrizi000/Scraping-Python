import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

# Carpeta donde se guardan los resultados
CARPETA_RESULTADOS = "/home/fabri/Documents/scrap/resultados"
os.makedirs(CARPETA_RESULTADOS, exist_ok=True)

def ejecutar_scraper():
    navegador = navegador_var.get()
    url = url_entry.get().strip()

    if not url:
        messagebox.showwarning("Error", "Por favor, ingresa un link")
        return

    # Determinar qué scraper usar y el nombre del archivo de salida
    if navegador == "Firefox":
        script = "firefox_engine.py"
        archivo_salida = os.path.join(CARPETA_RESULTADOS, "datos_scrapeadosFirefox.txt")
    elif navegador == "Chrome":
        script = "chrome_engine.py"
        archivo_salida = os.path.join(CARPETA_RESULTADOS, "datos_scrapeadosChrome.txt")
    else:
        messagebox.showerror("Error", "Navegador no soportado")
        return

    # Ejecutar el scraper
    try:
        resultado = subprocess.run(
            ["python3", script, url],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            check=True
        )
        # Abrir el archivo de resultados automáticamente
        if os.path.exists(archivo_salida):
            subprocess.run(["xdg-open", archivo_salida])
        else:
            messagebox.showwarning("Atención", f"No se encontró el archivo: {archivo_salida}")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"El scraper falló:\n{e}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# --- GUI ---
root = tk.Tk()
root.title("WEB BUSTER")
root.geometry("450x200")

tk.Label(root, text="URL para scrapear:").pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

tk.Label(root, text="Selecciona navegador:").pack(pady=5)
navegador_var = tk.StringVar(value="Firefox")
navegador_combo = ttk.Combobox(root, textvariable=navegador_var, values=["Firefox", "Chrome"])
navegador_combo.pack(pady=5)

tk.Button(root, text="Ejecutar Scraper", command=ejecutar_scraper).pack(pady=20)

root.mainloop()
