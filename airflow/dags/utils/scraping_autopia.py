"""
scraping_autopia.py

Script de scraping para extraer publicaciones de vehículos desde autopia.com.bo.

Utiliza Playwright en modo sincrónico para navegar por el sitio, cargar dinámicamente todos los anuncios
y acceder a las páginas de detalle para recolectar características específicas del vehículo.

"""

from playwright.sync_api import sync_playwright
import pandas as pd
from urllib.parse import urljoin
import time
import os
from datetime import datetime

BASE_URL = "https://www.autopia.com.bo"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # sube desde /utils a /dags
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_CSV = os.path.join(RAW_DATA_DIR, f"scraped_autopia_{datetime.now().strftime('%Y-%m-%d')}.csv")


EXPECTED_FIELDS = ["Km", "Motor", "Año", "Tipo", "Combustible", "Color", "Transmisión", "Puertas"]

def parse_detail_page(page):
    """
    Extrae detalles específicos del vehículo desde una página individual.
    Args:
        page (playwright.Page): Página web de un anuncio individual.
    Returns:
        dict: Diccionario con los campos estandarizados encontrados en la página.
    """
    details = {field.lower().replace('é','e').replace('á','a').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n').replace(' ', '_'): None for field in EXPECTED_FIELDS}
    paras = page.locator("p")
    for i in range(paras.count()):
        text = paras.nth(i).inner_text().strip()
        for field in EXPECTED_FIELDS:
            if text.startswith(f"{field}:"):
                value = text.split(":", 1)[1].strip()
                key = field.lower().replace('é','e').replace('á','a').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n').replace(' ', '_')
                details[key] = value
    return details

def load_all_listings(page):
    """Hace clic en 'Cargar más' mientras sigan apareciendo más autos."""
    prev_count = 0

    while True:
        listings = page.locator("a", has_text="$")
        current_count = listings.count()

        if current_count == prev_count:
            print("✅ Ya no se cargan más autos, detenemos los clics.")
            break

        try:
            # Buscar el botón contenedor del texto
            load_more_button = page.locator("button p", has_text="Cargar más").locator("..")

            if load_more_button.is_visible():
                print("🔁 Clic en 'Cargar más'")
                load_more_button.click()
                time.sleep(1.5)
                prev_count = current_count
            else:
                print("✅ Botón 'Cargar más' no está visible, fin del scroll.")
                break
        except Exception as e:
            print(f"❌ Error al interactuar con el botón: {e}")
            break

def scrape_all(ctx):
    """
    Carga todos los anuncios, accede a sus páginas de detalle y extrae información estructurada.
    Args:
        ctx (playwright.BrowserContext): Contexto de navegación de Playwright.
    Returns:
        list[dict]: Lista de registros de autos con campos generales y detallados.
    """
    page = ctx.new_page()
    page.goto(BASE_URL + "/resultados", wait_until="networkidle")
    page.wait_for_selector("a", timeout=10000)

    load_all_listings(page)  # Hace clics hasta que no haya más autos

    listings = page.locator("a", has_text="$")
    total = listings.count()
    print(f"➡️ Total de publicaciones visibles: {total}")

    records = []
    for idx in range(total):
        link = listings.nth(idx)
        href = link.get_attribute("href") or ""
        detail_url = urljoin(BASE_URL, href)
        text = link.inner_text().strip()

        try:
            loc_model, rest = [s.strip() for s in text.split("|", 1)]
            year, price = rest.split()[:2]
        except ValueError:
            parts = text.split()
            loc_model = " ".join(parts[:-2])
            year = parts[-2]
            price = parts[-1]

        city, brand, *model_parts = loc_model.split()
        model = " ".join(model_parts)

        detail_page = ctx.new_page()
        detail_page.goto(detail_url, wait_until="networkidle")
        time.sleep(1)
        details = parse_detail_page(detail_page)
        detail_page.close()

        record = {
            "city": city, "brand": brand, "model": model,
            "year": year, "price": price, "detail_url": detail_url,
            **details
        }
        print(f"✔️ Anuncio {idx + 1}/{total}")
        records.append(record)
    page.close()
    return records

def run_scraper():
    """
    Función principal para ejecutar el scraping y guardar los resultados en un archivo .csv.
    """
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()

        records = scrape_all(ctx)
        df = pd.DataFrame(records)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"✅ Guardado final: {OUTPUT_CSV} con {len(df)} registros.")

        browser.close()
    print(f"✅ Scraping terminado. Guardado en {OUTPUT_CSV}")
