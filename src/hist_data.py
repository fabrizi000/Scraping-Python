import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Leer el CSV
df = pd.read_csv("C:/Users/manuel/Documents/python/t6.csv")

# Limpiar nombres de columnas
df.columns = df.columns.str.strip().str.lower()

# -----------------------------
# Selección de columna
# -----------------------------
print("¿Qué dato quieres mostrar?")
print("1 - Actual")
print("2 - Prevision")
print("3 - Anterior")

opcion = input("Selecciona 1, 2 o 3: ").strip()

if opcion == "1":
    columna = "actual"
elif opcion == "2":
    columna = "prevision"
elif opcion == "3":
    columna = "anterior"
else:
    print("Opción no válida")
    exit()

# -----------------------------
# Tipo de valor
# -----------------------------
print("\n¿Qué tipo de valores quieres representar?")
print("1 - Porcentaje (%)")
print("2 - Miles (K)")
print("3 - Miles de millones (B)")

tipo = input("Selecciona 1, 2 o 3: ").strip()

if tipo not in ["1", "2", "3"]:
    print("Opción no válida")
    exit()

# -----------------------------
# Función de conversión
# -----------------------------
def parse_valor(val):
    if pd.isna(val):
        return np.nan

    s = str(val).strip()

    if s in ["--", "", "nan"]:
        return np.nan

    # Cambiar coma por punto decimal
    s = s.replace(",", ".")

    try:
        # Porcentaje
        if tipo == "1":
            if "%" not in s:
                return np.nan
            return float(s.replace("%", ""))

        # Miles (K)
        if tipo == "2":
            if "K" not in s:
                return np.nan
            return float(s.replace("K", ""))

        # Miles de millones (B)
        if tipo == "3":
            if "B" not in s:
                return np.nan
            return float(s.replace("B", ""))

    except:
        return np.nan

# -----------------------------
# Convertir columna
# -----------------------------
df["valor_num"] = df[columna].apply(parse_valor)

# Eliminar NaN y ceros
df = df.dropna(subset=["valor_num"])
df = df[df["valor_num"] != 0]

# -----------------------------
# COMPROBAR SI HAY DATOS
# -----------------------------
if df.empty:
    print("No hay datos con ese filtro")
    exit()

# -----------------------------
# GRÁFICO
# -----------------------------
y_min = df["valor_num"].min()
y_max = df["valor_num"].max()

# Evitar rango cero
if y_min == y_max:
    y_min -= 1
    y_max += 1

x = np.arange(1, len(df) + 1)

# Colores según signo
colores = ["#90EE90" if v >= 0 else "#FF7F7F" for v in df["valor_num"]]

plt.figure(figsize=(14, 6))
plt.bar(x, df["valor_num"], color=colores)
plt.xticks(x)
plt.ylim(y_min, y_max)
plt.xlabel("Índice")
plt.ylabel(columna)

# Línea horizontal en cero
plt.axhline(0, color="black", linewidth=1)

# Título según tipo
if tipo == "1":
    titulo = "Porcentajes (%)"
elif tipo == "2":
    titulo = "Miles (K)"
else:
    titulo = "Miles de millones (B)"

plt.title(f"{columna} - {titulo}")

# -----------------------------
# TABLA DE EVENTOS
# -----------------------------
evento_col = "evento"

df["numero"] = range(1, len(df) + 1)
tabla = df[[evento_col, "numero"]]

fig_height = max(10, len(tabla) * 0.3)
fig, ax = plt.subplots(figsize=(12, fig_height))
ax.axis("off")

table = ax.table(
    cellText=tabla.values,
    colLabels=["Evento", "Número"],
    cellLoc="center",
    loc="center"
)

table.auto_set_font_size(False)
table.set_fontsize(min(13, 400 / len(tabla)))
table.auto_set_column_width([0, 1])

plt.tight_layout()
plt.show()
