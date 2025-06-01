from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

from scraping_autopia import run_scraper

with DAG(
    dag_id="scraping_autopia_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["scraping", "autopia"]
) as dag:

    scrape_task = PythonOperator(
        task_id="scrapear_datos_autopia",
        python_callable=run_scraper
    )

    # disparar DAG de entrenamiento
    trigger_entrenamiento = TriggerDagRunOperator(
        task_id="trigger_entrenamiento",
        trigger_dag_id="entrenamiento_modelos_regresion",  # ✅ Correcto
        wait_for_completion=True
    )

    scrape_task >> trigger_entrenamiento  # ✅ Esta es la manera correcta
