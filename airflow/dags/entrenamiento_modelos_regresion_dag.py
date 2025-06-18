'''
3er Dag de entrenamiento, posterior al de preprocesamiento.
Este DAG entrena modelos de regresión sobre un dataset de autos usados,
selecciona el mejor modelo según el MAE, lo registra en MLflow y lo promueve a producción.  
'''

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
    dag_id="entrenamiento_modelos_regresion",
    default_args=default_args,
    schedule_interval="0 21 * * *",  # 17:00 UTC-4 = 21:00 UTC
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["regresion", "mlflow", "mlops"]
)
def train_and_promote_models():
    """
    DAG que orquesta el proceso de entrenamiento de tres modelos de regresión 
    (RandomForest, GradientBoosting, SVR), selecciona el mejor según el MAE, 
    lo registra en MLflow y lo promueve automáticamente a producción.
    Luego, dispara un segundo DAG encargado de hacer predicciones con el modelo promovido.
    """

    @task()
    def entrenar_y_promover():
        """
        Tarea que entrena múltiples modelos de regresión sobre un dataset de autos usados,
        compara su desempeño con MAE, registra el mejor modelo en MLflow y lo promueve
        a la etapa de producción. Los modelos considerados son RandomForest, GradientBoosting y SVR.
        """
        import pandas as pd
        import mlflow
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
        from sklearn.svm import SVR
        from sklearn.metrics import mean_absolute_error
        from mlflow.tracking import MlflowClient
        from category_encoders import TargetEncoder

        df = pd.read_pickle("/opt/airflow/dags/data/processed/autopia_dataset.pkl")

        # Features y encoding
        X = df[["model", "year", "km", "motor", "tipo", "transmision", "puertas"]]
        y = df["price"]

        marca_encoder = TargetEncoder()
        X["marca_encoded"] = marca_encoder.fit_transform(X["model"], y)

        tipo_encoder = TargetEncoder()
        X["tipo_encoded"] = tipo_encoder.fit_transform(X["tipo"], y)

        X["Transmision_encoded"] = X["transmision"].map({"Mecánico": 0, "Automático": 1})
        X.drop(columns=["model", "transmision", "tipo"], inplace=True)

        # Split de datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Guardar los encoders para uso en predicción
        import joblib

        preprocessing_dir = "/opt/airflow/dags/data/processed/encoders/"
        os.makedirs(preprocessing_dir, exist_ok=True)

        joblib.dump(marca_encoder, os.path.join(preprocessing_dir, "marca_encoder.pkl"))
        joblib.dump(tipo_encoder, os.path.join(preprocessing_dir, "tipo_encoder.pkl"))

        # Configuración de MLflow
        mlflow.set_tracking_uri("http://mlflow:5000")
        mlflow.set_experiment("entrenamiento_orquestado")

        modelos = {
            "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
            "GradientBoosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
            "SVR": SVR()
        }

        best_score = float("inf")
        best_model_uri = None
        best_name = "mejor_modelo_orquestado"
        client = MlflowClient()

        # Entrenamiento, evaluación y logging
        for nombre, modelo in modelos.items():
            with mlflow.start_run(run_name=nombre):
                modelo.fit(X_train, y_train)
                y_pred = modelo.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)

                mlflow.log_param("modelo", nombre)
                mlflow.log_metric("mae", mae)
                mlflow.sklearn.log_model(modelo, "modelo")

                if mae < best_score:
                    best_score = mae
                    best_model_uri = f"runs:/{mlflow.active_run().info.run_id}/modelo"

        # Registrar y promover el mejor modelo
        result = mlflow.register_model(model_uri=best_model_uri, name=best_name)
        versions = client.get_latest_versions(best_name)

        for v in versions:
            if v.version == result.version:
                client.transition_model_version_stage(
                    name=best_name,
                    version=v.version,
                    stage="Production",
                    archive_existing_versions=True
                )
            else:
                client.transition_model_version_stage(
                    name=best_name,
                    version=v.version,
                    stage="Staging"
                )

    # Crear la tarea de entrenamiento
    entrenamiento = entrenar_y_promover()

    # Operador para disparar el DAG de predicción
    trigger_prediccion = TriggerDagRunOperator(
        task_id="trigger_prediccion",
        trigger_dag_id="prediccion_modelo_produccion_dag",
        wait_for_completion=False
    )

    # Definir el orden de ejecución
    entrenamiento >> trigger_prediccion

# Instanciar el DAG
dag = train_and_promote_models()
