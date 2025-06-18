'''
Segundo DAG, luego de scrapping y guardando los CSVs, este DAG se encarga de:

1. Combinar todos los CSVs descargados en un único DataFrame.
2. Aplicar limpieza y validación básica.'''

from airflow.decorators import dag, task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
import os

default_args = {
    "owner": "fede",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

@dag(
    dag_id="procesamiento_datos_autopia_dag",
    default_args=default_args,
    schedule_interval=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["procesamiento", "autos", "mlops"]
)
def procesar_y_preparar_datos():
    """
    DAG que concatena todos los CSVs descargados, aplica limpieza y validación básica,
    y guarda un archivo .pkl listo para el entrenamiento de modelos. Luego activa el DAG de entrenamiento.
    """

    @task()
    def combinar_y_limpiar():
        import pandas as pd
        import glob

        raw_dir = "/opt/airflow/dags/data/raw/"
        output_path = "/opt/airflow/dags/data/processed/autopia_dataset.pkl"

        all_csvs = glob.glob(os.path.join(raw_dir, "*.csv"))
        if not all_csvs:
            raise FileNotFoundError("No se encontraron archivos .csv en el directorio raw.")

        df_list = [pd.read_csv(file) for file in all_csvs]
        df = pd.concat(df_list, ignore_index=True)

        # Validación mínima
        df.dropna(subset=['motor', 'price'], inplace=True)

        df['price'] = df['price'].astype(str).str.replace('$', '').str.replace(',', '.').astype(float) * 1000
        df['motor'] = df['motor'].astype(str).str.replace('Lt.', '').replace('.', ',').astype(float)

        # Eliminamos duplicados - de distintas descargas pueden haber registros repetidos
        df.drop_duplicates(subset='detail_url', inplace=True)
        
        # Guardamos el DataFrame limpio en formato .pkl
        df.to_pickle(output_path)
        print(f"Dataset combinado y limpio guardado en: {output_path}")

    combinar = combinar_y_limpiar()

    # Disparar DAG de entrenamiento
    trigger_entrenamiento = TriggerDagRunOperator(
        task_id="trigger_entrenamiento",
        trigger_dag_id="entrenamiento_modelos_regresion",
        wait_for_completion=True
    )

    combinar >> trigger_entrenamiento

dag = procesar_y_preparar_datos()
