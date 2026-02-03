import tkinter as tk
from tkinter import ttk
import webbrowser

# ==========================
# DATOS DE LAS PÁGINAS
# ==========================
PAGINAS = {
    "Selecciona una página": {
        "url": "",
        "calendario": False
    },
    "Investing – Economic Calendar": {
        "url": "https://www.investing.com/economic-calendar/",
        "calendario": True
    },
    "World Government Bonds": {
        "url": "https://www.worldgovernmentbonds.com/",
        "calendario": False
    },
    "Reuters – Economic News": {
        "url": "https://www.reuters.com/world/",
        "calendario": False
    },
    "BBC – Business News": {
        "url": "https://www.bbc.com/news/business",
        "calendario": False
    },
    "Yahoo Finance – News": {
        "url": "https://finance.yahoo.com/news/",
        "calendario": False
    }
}

# ==========================
# FUNCIONES
# ==========================
def pagina_seleccionada(event=None):
    pagina = combo_pagina.get()
    info = PAGINAS[pagina]

    # Mostrar URL
    url_var.set(info["url"])

    # Mostrar u ocultar opciones de calendario
    if info["calendario"]:
        frame_calendario.pack(pady=15)
    else:
        frame_calendario.pack_forget()

    # Mostrar botón SCRAPEAR solo si hay página válida
    if pagina != "Selecciona una página":
        btn_scrapear.pack(pady=25)
    else:
        btn_scrapear.pack_forget()


def abrir_url():
    if url_var.get():
        webbrowser.open(url_var.get())


def scrapear():
    print("=== WEB BUSTER ===")
    print("Página:", combo_pagina.get())
    print("URL:", url_var.get())

    if frame_calendario.winfo_ismapped():
        print("Fecha:", entry_fecha.get())
        print("Impacto:", combo_impacto.get())

    print("Aquí se llamaría al scraper real")


# ==========================
# VENTANA PRINCIPAL
# ==========================
root = tk.Tk()
root.title("WEB BUSTER")
root.geometry("540x500")
root.resizable(False, False)

# ==========================
# TÍTULO
# ==========================
tk.Label(
    root,
    text="WEB BUSTER",
    font=("Arial", 20, "bold")
).pack(pady=(15, 5))

tk.Label(
    root,
    text="Scraper para páginas de Economía",
    font=("Arial", 11)
).pack()

# ==========================
# SELECCIÓN DE PÁGINA
# ==========================
frame_pagina = tk.Frame(root)
frame_pagina.pack(pady=20)

tk.Label(frame_pagina, text="Página a scrapear:").pack(anchor="w")

combo_pagina = ttk.Combobox(
    frame_pagina,
    values=list(PAGINAS.keys()),
    state="readonly",
    width=48
)
combo_pagina.current(0)
combo_pagina.configure(takefocus=0)
combo_pagina.pack()
combo_pagina.bind("<<ComboboxSelected>>", pagina_seleccionada)

# ==========================
# URL VISIBLE
# ==========================
frame_url = tk.Frame(root)
frame_url.pack(pady=10)

tk.Label(frame_url, text="URL seleccionada:").pack(anchor="w")

url_var = tk.StringVar()
tk.Entry(
    frame_url,
    textvariable=url_var,
    width=48,
    state="readonly"
).pack(side="left")

tk.Button(
    frame_url,
    text="Abrir",
    command=abrir_url
).pack(side="left", padx=5)

# ==========================
# OPCIONES DE CALENDARIO
# ==========================
frame_calendario = tk.Frame(root)

tk.Label(frame_calendario, text="Fecha (YYYY-MM-DD):").pack(anchor="w")
entry_fecha = tk.Entry(frame_calendario, width=20)
entry_fecha.insert(0, "2020-01-01")
entry_fecha.pack()

tk.Label(frame_calendario, text="Impacto:").pack(anchor="w", pady=(10, 0))
combo_impacto = ttk.Combobox(
    frame_calendario,
    values=["1", "2", "3"],
    state="readonly",
    width=5
)
combo_impacto.current(1)
combo_impacto.pack()

# ==========================
# BOTÓN SCRAPEAR (AL FINAL)
# ==========================
btn_scrapear = tk.Button(
    root,
    text="SCRAPEAR",
    font=("Arial", 12, "bold"),
    width=20,
    command=scrapear
)

root.mainloop()