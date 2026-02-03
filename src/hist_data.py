import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Leer el CSV
df = pd.read_csv("/home/alusmr/Documentos/python2/t2.csv")

# Preguntar qué columna usar
print("¿Qué dato quieres mostrar?")
print("1 - Actual")
print("2 - Prevision")
print("3 - Anterior")

opcion = input("Selecciona 1, 2 o 3: ").strip()

if opcion == "1":
    columna = "Actual"
elif opcion == "2":
    columna = "Prevision"
elif opcion == "3":
    columna = "Anterior"
else:
    print("Opción no válida")
    exit()

# Preguntar qué tipo de valores mostrar
print("\n¿Qué tipo de valores quieres representar?")
print("1 - Porcentaje (%)")
print("2 - Miles (K)")


tipo = input("Selecciona 1, 2 o 3: ").strip()

# Función de conversión
def parse_valor(val):
    if pd.isna(val):
        return np.nan

    s = str(val).strip()

    if s in ["--", "", "nan"]:
        return np.nan

    # Filtrado por tipo
    if tipo == "1" and "%" not in s:
        return np.nan
    if tipo == "2" and "K" not in s:
        return np.nan

    s = s.replace("%", "")
    s = s.replace("K", "")
    s = s.replace(",", ".")

    try:
        return float(s)
    except:
        return np.nan

# Convertir columna
df["valor_num"] = df[columna].apply(parse_valor)

# Eliminar ceros y NaN
df = df.dropna(subset=["valor_num"])
df = df[df["valor_num"] != 0]

# Límites reales del eje Y
y_min = df["valor_num"].min()
y_max = df["valor_num"].max()


x = np.arange(1, len(df) + 1)

plt.figure(figsize=(14, 6))
plt.bar(x, df["valor_num"])
plt.xticks(x)
plt.ylim(y_min, y_max)
plt.xlabel("Índice")
plt.ylabel(columna)
plt.title(f"{columna} filtrado por tipo de valor")

#----------------------------------------------------------------------------------------------------------------------

df.columns = df.columns.str.strip()

# Detectar la columna que contiene "Evento"
evento_col = [col for col in df.columns if 'evento' in col.lower()]
if not evento_col:
    raise ValueError("No se encontró la columna 'Evento' en el CSV")
evento_col = evento_col[0]

# -----------------------------
# Crear columna de números consecutivos
# -----------------------------
df['Número'] = range(1, len(df) + 1)

# Seleccionar solo las columnas necesarias
tabla = df[[evento_col, 'Número']]

# -----------------------------
# Crear figura y tabla
# -----------------------------
# Ajusta tamaño según número de filas (más filas -> figura más alta)
fig_height = max(10, len(tabla)*0.3)
fig, ax = plt.subplots(figsize=(12, fig_height))
ax.axis('off')  # Quitar ejes

# Crear la tabla
table = ax.table(
    cellText=tabla.values,
    colLabels=[evento_col, 'Número'],
    cellLoc='center',
    loc='center'
)

# Ajustar fuente para que se vea mejor según número de filas
table.auto_set_font_size(False)
table.set_fontsize(min(13, 400/len(tabla)))  # tamaño automático según filas

# Ajustar altura de las celdas para que no se superpongan
table.auto_set_column_width([0, 1])

plt.tight_layout()
plt.show()






plt.tight_layout()
plt.show()



