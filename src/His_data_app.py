import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from textwrap import wrap

# ---------------- PARSE VALORES ----------------
def parse_valor(val, tipo):
    if pd.isna(val):
        return np.nan
    s = str(val).strip()
    if s in ["--", "", "nan"]:
        return np.nan
    s = s.replace(",", ".")
    try:
        if tipo == "1":
            if "%" not in s:
                return np.nan
            return float(s.replace("%", ""))
        elif tipo == "2":
            if "K" not in s:
                return np.nan
            return float(s.replace("K", ""))
        elif tipo == "3":
            if "B" not in s:
                return np.nan
            return float(s.replace("B", ""))
    except:
        return np.nan


# ---------------- CARGAR CSV DATOS ----------------
def cargar_csv():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip().str.lower()
        messagebox.showinfo("Éxito", f"Archivo cargado:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar:\n{e}")


# ---------------- GENERAR GRÁFICO ----------------
def generar_grafico():
    if df is None:
        messagebox.showwarning("Sin archivo", "Primero carga un CSV")
        return

    columna_map = {"Actual": "actual", "Prevision": "prevision", "Anterior": "anterior"}
    tipo_map = {"Porcentaje (%)": "1", "Miles (K)": "2", "Miles de millones (B)": "3"}

    columna = columna_map[columna_var.get()]
    tipo_val = tipo_map[tipo_var.get()]

    df["valor_num"] = df[columna].apply(lambda v: parse_valor(v, tipo_val))
    df_filtrado = df.dropna(subset=["valor_num"])
    df_filtrado = df_filtrado[df_filtrado["valor_num"] != 0]

    if df_filtrado.empty:
        messagebox.showwarning("Sin datos", "No hay datos con ese filtro")
        return

    # Limpiar scroll anterior
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # ----------- HISTOGRAMA -----------
    y_min = df_filtrado["valor_num"].min()
    y_max = df_filtrado["valor_num"].max()
    if y_min == y_max:
        y_min -= 1
        y_max += 1

    x = np.arange(1, len(df_filtrado) + 1)
    colores = ["#90EE90" if v >= 0 else "#FF7F7F" for v in df_filtrado["valor_num"]]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(x, df_filtrado["valor_num"], color=colores)
    ax.set_xticks(x)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("Índice")
    ax.set_ylabel(columna)
    ax.axhline(0, color="black")
    titulo_map = {"1": "Porcentajes (%)", "2": "Miles (K)", "3": "Miles de millones (B)"}
    ax.set_title(f"{columna} - {titulo_map[tipo_val]}")

    frame_grafico = tk.Frame(scrollable_frame)
    frame_grafico.pack(fill="both", expand=True, pady=10)
    canvas_fig = FigureCanvasTkAgg(fig, master=frame_grafico)
    canvas_fig.draw()
    canvas_fig.get_tk_widget().pack(anchor="center")

    # ----------- TABLA EVENTOS -----------
    df_filtrado["numero"] = range(1, len(df_filtrado) + 1)
    tabla = df_filtrado[["evento", "numero"]]

    fig_tabla, ax_tabla = plt.subplots(figsize=(10, max(2, len(tabla) * 0.3)))
    ax_tabla.axis("off")
    table = ax_tabla.table(
        cellText=tabla.values,
        colLabels=["Evento", "Número"],
        cellLoc="center",
        loc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(min(13, 400 / len(tabla)))
    table.auto_set_column_width([0, 1])

    frame_tabla = tk.Frame(scrollable_frame)
    frame_tabla.pack(fill="both", expand=True, pady=10)
    canvas_tabla = FigureCanvasTkAgg(fig_tabla, master=frame_tabla)
    canvas_tabla.draw()
    canvas_tabla.get_tk_widget().pack(anchor="center")

    scrollable_canvas.update_idletasks()
    scrollable_canvas.config(scrollregion=scrollable_canvas.bbox("all"))


# ---------------- CARGAR NOTICIAS ----------------
def cargar_noticias():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return

    try:
        noticias = []
        with open(file_path, newline="", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                noticias.append(fila)

        if not noticias:
            messagebox.showwarning("Sin noticias", "CSV vacío")
            return

        frame_noticias = tk.Frame(scrollable_frame)
        frame_noticias.pack(fill="both", expand=True, pady=20)

        titulo_label = tk.Label(frame_noticias, text="📰 NOTICIAS DEL DÍA", font=("Arial", 20, "bold"))
        titulo_label.pack()

        frame_text = tk.Frame(frame_noticias)
        frame_text.pack(fill="both", expand=True)

        scroll = tk.Scrollbar(frame_text)
        scroll.pack(side="right", fill="y")

        text_widget = tk.Text(frame_text, yscrollcommand=scroll.set, font=("Arial", 12), wrap="word", height=20)
        text_widget.pack(fill="both", expand=True)

        scroll.config(command=text_widget.yview)
        text_widget.tag_configure("titulo", font=("Arial", 16, "bold"))

        for n in noticias:
            titulo = n.get("titulo", "")
            resumen = n.get("resumen", "")

            if titulo:
                text_widget.insert("end", titulo + "\n", "titulo")
                text_widget.insert("end", "\n")

            if resumen:
                for linea in wrap(resumen, 120):
                    text_widget.insert("end", linea + "\n")

                text_widget.insert("end", "\n" + "-" * 100 + "\n\n")

        text_widget.config(state="disabled")

        scrollable_canvas.update_idletasks()
        scrollable_canvas.config(scrollregion=scrollable_canvas.bbox("all"))

    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar noticias:\n{e}")


# ---------------- TKINTER UI ----------------
df = None

root = tk.Tk()
root.title("Visualizador de Datos CSV + Noticias")
root.geometry("1200x900")

tk.Button(root, text="Cargar CSV datos", command=cargar_csv).pack(pady=5)

columna_var = tk.StringVar(value="Actual")
tk.Label(root, text="Selecciona columna:").pack()
ttk.Combobox(root, textvariable=columna_var, values=["Actual", "Prevision", "Anterior"], state="readonly").pack()

tipo_var = tk.StringVar(value="Porcentaje (%)")
tk.Label(root, text="Selecciona tipo:").pack()
ttk.Combobox(root, textvariable=tipo_var, values=["Porcentaje (%)", "Miles (K)", "Miles de millones (B)"], state="readonly").pack()

tk.Button(root, text="Generar gráfico", command=generar_grafico).pack(pady=10)
tk.Button(root, text="Cargar noticias", command=cargar_noticias).pack(pady=5)

# -------- Scrollable Area --------
frame_scroll = tk.Frame(root)
frame_scroll.pack(fill="both", expand=True)

scrollable_canvas = tk.Canvas(frame_scroll)
scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=scrollable_canvas.yview)
scrollable_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
scrollable_canvas.pack(side="left", fill="both", expand=True)

scrollable_frame = tk.Frame(scrollable_canvas)
scrollable_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def on_frame_configure(event):
    scrollable_canvas.configure(scrollregion=scrollable_canvas.bbox("all"))

scrollable_frame.bind("<Configure>", on_frame_configure)

root.mainloop()
