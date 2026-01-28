from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os

# --- CONFIGURACIÓN DE RUTA ---
home_dir = os.path.expanduser("~")
ruta_completa = "/home/alusmr/Documentos/datos_investing.csv"


# --- CONFIGURACIÓN DE DRIVER ---
geckodriver_path = "/usr/local/bin/geckodriver"
service = Service(executable_path=geckodriver_path)

options = Options()
# options.add_argument("--headless")  # Descomenta si no quieres abrir ventana
options.binary_location = "/usr/bin/firefox"  # Ruta de tu Firefox

driver = webdriver.Firefox(service=service, options=options)

def extract_table_data(table_rows, categoria):
    data = []
    for row in table_rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 4:
            row_data = {
                'Categoria': categoria, 
                'Nombre/Empresa': cells[0].text.strip(),
                'EPS (Previsto)': cells[1].text.strip(),
                'Ingresos (Previsto)': cells[2].text.strip(),
                'Market Cap': cells[3].text.strip()
            }
            data.append(row_data)
    return data

try:
    print("Abriendo Investing.com...")
    driver.get("https://www.investing.com/earnings-calendar/")
    
    wait = WebDriverWait(driver, 20)
    todos_los_datos = []

    #Este trozo extrae las paginas de HOY
    print("Obteniendo los datos de HOY...")
    wait.until(EC.presence_of_element_located((By.ID, "earningsCalendarData")))
    rows_today = driver.find_elements(By.CSS_SELECTOR, "#earningsCalendarData tbody tr")
    todos_los_datos.extend(extract_table_data(rows_today[:15], "Hoy"))

    #Este trozo son las para cambiar a la tabla  de esta semana
    print("Obteniendo datos de 'Esta semana'...")
    this_week_btn = wait.until(EC.element_to_be_clickable((By.ID, "timeFrame_thisWeek")))
    driver.execute_script("arguments[0].click();", this_week_btn)

    time.sleep(3) #Espera  para que la tabla se refresque 
    
    #Aqui extraemos la tabla de esta semana
    print("Extrayendo datos de ESTA SEMANA...")
    rows_week = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#earningsCalendarData tbody tr")))
    todos_los_datos.extend(extract_table_data(rows_week[:15], "Esta Semana"))

    #Esto es la parte de codigo que falta para tener el archivo.csv
    if todos_los_datos:
        keys = todos_los_datos[0].keys()
        with open(ruta_completa, 'w', newline='', encoding='utf-8-sig') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(todos_los_datos)
        print(f"\n Éxito: Datos guardados en {ruta_completa}")
    else:
        print("\n No se encontraron datos para guardar.")

except Exception as e:
    print(f"Ocurrió un error: {e}")

finally:
    driver.quit()
