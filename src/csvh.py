import matplotlib
matplotlib.use("TkAgg")

import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv

df = None

# ---------- CONVERTIR VALORES ----------
def convertir(valor, tipo):
    try:
        t = str(valor).replace(",", ".").strip()
        if tipo == "Porcentaje (%)" and "%" in t:
            return float(t.replace("%", ""))
        if tipo == "K" and "K" in t:
            return float(t.replace("K", ""))
        if tipo == "B" and "B" in t:
            return float(t.replace("B", ""))
        return float(t)
    except:
        return np.nan

# ---------- CARGAR CSV ----------
def cargar_csv():
    global df
    ruta = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
    if ruta:
        df = pd.read_csv(ruta)
        df.columns = df.columns.str.lower()
        messagebox.showinfo("OK", "CSV cargado")

# ---------- MOSTRAR GRAFICO ----------
def mostrar_grafico():
    if df is None:
        messagebox.showerror("Error", "Carga un CSV")
        return

    columna = columna_var.get().lower()
    tipo = tipo_var.get()

    if columna not in df.columns:
        messagebox.showerror("Error", f"La columna '{columna}' no existe en el CSV")
        return

    datos = df.copy()
    datos["valor"] = datos[columna].apply(lambda x: convertir(x, tipo))
    datos = datos.dropna(subset=["valor"])

    if datos.empty:
        messagebox.showerror("Error", "No hay datos válidos para graficar")
        return

    x = np.arange(len(datos))
    etiquetas = datos.index + 1

    ventana = tk.Toplevel(root)
    ventana.title("Gráfico")
    ventana.geometry("900x600")

    fig = plt.Figure(figsize=(10, 4), dpi=100)
    ax = fig.add_subplot(111)

    colores = ["green" if v >= 0 else "red" for v in datos["valor"]]

    ax.bar(x, datos["valor"], color=colores)
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, rotation=45)
    ax.set_title(columna)

    canvas = FigureCanvasTkAgg(fig, master=ventana)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    plt.close(fig)

    # ---------- LISTA EVENTOS ----------
    texto = tk.Text(ventana, height=10, font=("Consolas", 10))
    texto.pack(fill="both", expand=True)

    for i, fila in datos.iterrows():
        texto.insert("end", f"{i+1:>2} → {fila.get('evento', '')}\n")

    texto.config(state="disabled")

# ---------- NOTICIAS ----------
def mostrar_noticias():
    ruta = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
    if not ruta:
        return

    ventana = tk.Toplevel(root)
    ventana.title("Noticias")
    ventana.geometry("800x600")

    texto = tk.Text(ventana, wrap="word")
    texto.pack(fill="both", expand=True)

    with open(ruta, encoding="utf-8") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            texto.insert("end", fila.get("titulo", "") + "\n", "t")
            texto.insert("end", fila.get("resumen", "") + "\n\n")
            texto.insert("end", "-" * 50 + "\n\n")

    texto.tag_config("t", font=("Arial", 14, "bold"))
    texto.config(state="disabled")

# ---------- GUI ----------
root = tk.Tk()
root.title("CSV HUNTER")
root.geometry("420x260")

titulo_label = tk.Label(root, text="CSV HUNTER", font=("Arial", 18, "bold"))
titulo_label.pack(pady=(10, 0))

subtitulo_label = tk.Label(root, text="Visualizador de CSV (gráficos y noticias)", font=("Arial", 10))
subtitulo_label.pack(pady=(0, 10))

tk.Button(root, text="Cargar CSV datos", command=cargar_csv).pack(pady=5)

columna_var = tk.StringVar(value="Actual")
ttk.Combobox(
    root,
    textvariable=columna_var,
    values=["Actual", "Prevision", "Anterior"],
    state="readonly"
).pack()

tipo_var = tk.StringVar(value="Porcentaje (%)")
ttk.Combobox(
    root,
    textvariable=tipo_var,
    values=["Porcentaje (%)", "K", "B"],
    state="readonly"
).pack()

tk.Button(root, text="Ver gráfico", command=mostrar_grafico).pack(pady=10)
tk.Button(root, text="Ver noticias", command=mostrar_noticias).pack()

root.mainloop()
