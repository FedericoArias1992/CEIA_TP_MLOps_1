from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime
import sys
import os

# Agregar el directorio de utilidades al path para importar funciones personalizadas
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

from scraping_autopia import run_scraper

# Definición del DAG de scraping
with DAG(
    dag_id="scraping_autopia_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Este DAG se ejecuta bajo demanda
    catchup=False,
    tags=["scraping", "autopia"]
) as dag:
    """
    DAG que ejecuta un scraper para extraer datos del sitio Autopia.
    Al completar el scraping, desencadena el DAG de entrenamiento de modelos.
    """

    scrape_task = PythonOperator(
        task_id="scrapear_datos_autopia",
        python_callable=run_scraper,
        doc_md="""
        ### scrape_task
        Esta tarea ejecuta el proceso de scraping definido en `scraping_autopia.py`, 
        almacenando los datos en formato CSV para su posterior procesamiento.
        """
    )

    # disparar DAG de procesamiento de datos
    trigger_procesamiento = TriggerDagRunOperator(
        task_id="trigger_procesamiento",
        trigger_dag_id="procesamiento_datos_autopia_dag",
        wait_for_completion=True,
        doc_md="""
        ### trigger_procesamiento
        Esta tarea dispara el DAG `procesamiento_datos_autopia_dag` 
        una vez completado el scraping, concatena los .csv de distintas
        descargas, las concatena, elimina duplicados y parsea y limpia los registros.
        """
    )

    scrape_task >> trigger_procesamiento
