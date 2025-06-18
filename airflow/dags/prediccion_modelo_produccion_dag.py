'''
4to DAG, que no esta en funcionamiento, pero que se usaba para hacer
en lote, segun datos en la carpeta data/prediccion/nuevos_datos.csv'''

from airflow.decorators import dag, task
from datetime import datetime, timedelta

default_args = {
    "owner": "fede",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

@dag(
    dag_id="prediccion_modelo_produccion_dag",
    description="Predice con el modelo ganador en producción",
    schedule_interval="0 22 * * *",  # Todos los días a las 18:00 UTC-4
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["prediccion", "mlflow", "produccion"]
)
def hacer_predicciones():
    """
    DAG que realiza predicciones diarias utilizando el modelo ganador 
    que ha sido promovido a producción en MLflow.
    Lee un archivo de nuevos datos, aplica el modelo, y guarda los resultados
    en un archivo CSV de salida.
    """

    @task()
    def predecir():
        """
        Tarea que carga el modelo de producción desde MLflow, lee un archivo CSV 
        con datos nuevos para predecir, ejecuta la inferencia y guarda las predicciones 
        en un nuevo archivo CSV con una columna adicional.
        """
        import pandas as pd
        import mlflow.sklearn
        import os

        # Parámetros
        model_name = "mejor_modelo_orquestado"
        stage = "Production"
        input_path = "/opt/airflow/dags/data/prediccion/nuevos_datos.csv"
        output_path = "/opt/airflow/dags/data/prediccion/predicciones_resultados.csv"

        # Configurar tracking URI si se usa MLflow en contenedor
        mlflow.set_tracking_uri("http://mlflow:5000")

        # Cargar modelo desde el registry
        model = mlflow.sklearn.load_model(f"models:/{model_name}/{stage}")

        # Cargar datos
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"No se encontró el archivo: {input_path}")
        nuevos_datos = pd.read_csv(input_path, sep=';')

        # Hacer predicción
        predicciones = model.predict(nuevos_datos)

        # Guardar resultados
        nuevos_datos["prediccion"] = predicciones
        nuevos_datos.to_csv(output_path, index=False)

        print(f"✅ Predicciones guardadas en {output_path}")

    # Ejecutar la tarea
    predecir()

# Instancia del DAG
dag = hacer_predicciones()
