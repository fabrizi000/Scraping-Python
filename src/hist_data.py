import pandas as pd #Esto es para dataframe
import numpy as np #Esto es para cuando no tiene dato la empresa es decir cuando pone -- porque se scrapea asi
import re #Para limipiar texto
import matplotlib.pyplot as plt #Para hacer graficos

# Lee el csv
df = pd.read_csv("t2.csv")

# Esto es para convertir en un "numero" el market cap ya que se bugea pandas y no los coge bien

def parse_market_cap(val):
    if pd.isna(val):
        return np.nan #Si esta vacio devuelve NaN

    #Convertimos el valor a string y .strip() es para quitar espacios.
    s = str(val).strip()

    #Si el valor esta vacio lo ignora
    if s in ["--", "", "nan"]:
        return np.nan

    #Esta parte es solo para quitar caracteres que no hacen falta porque el scrapper coge todo en la pagina y algunos datos salen con letras al lado.
    s = re.sub(r"[^\d.,BMK]", "", s)

    #--------------------------------------------------------
    mult = 1
    if s.endswith("B"):
        mult = 1e9
        s = s[:-1]
    elif s.endswith("M"):
        mult = 1e6
        s = s[:-1]
    elif s.endswith("K"):
        mult = 1e3
        s = s[:-1]
    #--------------------------------------------------------

    #Elimina las comillas de los numeros.
    s = s.replace(",", "")

    #convierte la variable s en decimal si falla pues devuelve nada
    try:
        return float(s) * mult
    except:
        return np.nan

    
#seleccionamos la columna market cap del csv y utilizamos la clase de antes para aplicarle todos los cambios mencionados anteriormente.
df["MarketCap_num"] = df["Market Cap"].apply(parse_market_cap)

# Gráfico de barras 
#.figure para el tamaño de las barras
#.bar la parte (range(len(df)) es para recorrer el numero de columnas menos 1,el df MarketCap_num es para representar la altura de las barras.
#.xticks el (range(len(df)) espara la posicion x de las barras mientras que el  df["EPS (Previsto)"], rotation=90) es para poner las empresas y girarlas 90º
#.title para el titulo arriba
#.tight_layout es para ajustar las etiquetas para que todo este bien y no solape
#.show muestra el grafico

plt.figure(figsize=(12,6))
plt.bar(range(len(df)), df["MarketCap_num"])
plt.xticks(range(len(df)), df["EPS (Previsto)"], rotation=90)
plt.title("Market Cap por empresa")
plt.tight_layout()

plt.show()



