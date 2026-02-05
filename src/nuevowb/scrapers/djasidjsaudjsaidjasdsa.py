import tkinter as tk
import csv
from textwrap import wrap

# ---------------- LEER CSV ----------------
archivo_csv = "/home/fabri/Documents/WebBusterResultados/Elpais/elpais_resumen_20260205_113312.csv"

noticias = []

with open(archivo_csv, newline="", encoding="utf-8") as f:
    lector = csv.DictReader(f)
    columnas = lector.fieldnames
    print("Columnas detectadas:", columnas)

    for fila in lector:
        noticias.append(fila)

# ---------------- TKINTER ----------------
ventana = tk.Tk()
ventana.title("Noticias desde CSV")
ventana.geometry("900x600")

# Título principal de la app
titulo_app = tk.Label(
    ventana, text="NOTICIAS DEL DÍA", font=("Arial", 32, "bold"), pady=20
)
titulo_app.pack()

# Frame con scroll
frame = tk.Frame(ventana)
frame.pack(fill="both", expand=True)

scroll = tk.Scrollbar(frame)
scroll.pack(side="right", fill="y")

text_widget = tk.Text(frame, yscrollcommand=scroll.set, font=("Arial", 12), wrap="word")
text_widget.pack(fill="both", expand=True)

scroll.config(command=text_widget.yview)

# ---------------- TAG PARA EL TÍTULO DE CADA NOTICIA ----------------
text_widget.tag_configure("titulo", font=("Arial", 18, "bold"))  # Más grande y en negrita

# ---------------- MOSTRAR DATOS ----------------
for n in noticias:
    titulo = n.get("titulo", "")  # Tomar el título
    resumen = n.get("resumen", "")  # Tomar el resumen

    if titulo:
        # Insertar el título con formato
        text_widget.insert("end", titulo + "\n", "titulo")
        text_widget.insert("end", "\n")  # <-- Espacio extra entre título y resumen

    if resumen:
        # Insertar el resumen debajo
        lineas = wrap(resumen, 120)
        for linea in lineas:
            text_widget.insert("end", linea + "\n")

        # Separador entre noticias
        text_widget.insert("end", "\n" + "-" * 100 + "\n\n")

# Hacer que el Text sea de solo lectura
text_widget.config(state="disabled")

# Ejecutar
ventana.mainloop()