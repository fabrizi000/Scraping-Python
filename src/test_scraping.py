from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os

home_dir = os.path.expanduser("~")
ruta_completa = "/home/alusmr/Documentos/datos_investing.csv"

geckodriver_path = "/usr/local/bin/geckodriver"
service = Service(executable_path=geckodriver_path)

options = Options()
options.binary_location = "/usr/bin/firefox"

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

    print("\n¿Qué apartado quieres scrapear?")
    print("1 - Hoy")
    print("2 - Mañana")
    print("3 - Esta semana")
    print("4 - Semana que viene")
    print("5 - Ayer")

    opcion = input("Elige una opción (1-5): ").strip()

    wait.until(EC.presence_of_element_located((By.ID, "earningsCalendarData")))

    if opcion == "1":
        print("Obteniendo datos de HOY...")
        rows = driver.find_elements(By.CSS_SELECTOR, "#earningsCalendarData tbody tr")
        todos_los_datos.extend(extract_table_data(rows[:15], "Hoy"))

    elif opcion == "2":
        print("Cambiando a MAÑANA...")
        btn = wait.until(EC.element_to_be_clickable((By.ID, "timeFrame_tomorrow")))
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(3)

        print("Obteniendo datos de MAÑANA...")
        rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#earningsCalendarData tbody tr")))
        todos_los_datos.extend(extract_table_data(rows[:15], "Mañana"))

    elif opcion == "3":
        print("Cambiando a ESTA SEMANA...")
        btn = wait.until(EC.element_to_be_clickable((By.ID, "timeFrame_thisWeek")))
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(3)

        print("Obteniendo datos de ESTA SEMANA...")
        rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#earningsCalendarData tbody tr")))
        todos_los_datos.extend(extract_table_data(rows[:15], "Esta semana"))

    elif opcion == "4":
        print("Cambiando a PRÓXIMA SEMANA...")
        btn = wait.until(EC.element_to_be_clickable((By.ID, "timeFrame_nextWeek")))
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(3)

        print("Obteniendo datos de PRÓXIMA SEMANA...")
        rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#earningsCalendarData tbody tr")))
        todos_los_datos.extend(extract_table_data(rows[:15], "Próxima semana"))

    elif opcion == "5":
        print("Cambiando a AYER...")
        btn = wait.until(EC.element_to_be_clickable((By.ID, "timeFrame_yesterday")))
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(3)

        print("Obteniendo datos de AYER...")
        rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#earningsCalendarData tbody tr")))
        todos_los_datos.extend(extract_table_data(rows[:15], "Ayer"))

    else:
        print("Opción no válida.")

    # GUARDAR CSV
    if todos_los_datos:
        keys = todos_los_datos[0].keys()
        with open(ruta_completa, 'w', newline='', encoding='utf-8-sig') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(todos_los_datos)
        print(f"\nÉxito: Datos guardados en {ruta_completa}")
    else:
        print("\nNo se encontraron datos para guardar.")

except Exception as e:
    print(f"Ocurrió un error: {e}")

finally:
    driver.quit()
