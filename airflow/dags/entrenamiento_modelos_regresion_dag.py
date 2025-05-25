from airflow.decorators import dag, task
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

    @task()
    def entrenar_y_promover():
        import pandas as pd
        import mlflow
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestRegressor
        from catboost import CatBoostRegressor
        from sklearn.svm import SVR
        from sklearn.metrics import mean_absolute_error
        from mlflow.tracking import MlflowClient

        df = pd.read_pickle("/opt/airflow/dags/data/processed/autos_usados_limpios_20250524_2112.pkl")

        df['Tipo'] = df['Tipo'].str.replace(' ', '')
        df['Transmisión'] = df['Transmisión'].str.replace(' ', '')
        df.dropna(subset=["marca", "Motor", "Año","Tipo", "Transmisión"], inplace=True)
        #df['Año'] = df['Año'].str.replace(' ', '').astype(int)
        # 🎯 Selección de features (ajustá según tu dataset)
        X = df[["marca", "Motor", "Año","Tipo", "Transmisión"]]  # ← tus features reales
        y = df["precio"]

        from category_encoders import TargetEncoder
        '''Asocia cada marca con la media del target (ej. precio promedio del auto).

        Preserva orden y relevancia estadística.'''
        # Usá TargetEncoder si querés aprovechar la relación entre Tipo y el target (por ejemplo, precio del auto):
        # sirve para la marca y para el tipo de auto

        marca_encoder = TargetEncoder()
        X["marca_encoded"] = marca_encoder.fit_transform(X["marca"], y)

        tipo_encoder = TargetEncoder()
        X["tipo_encoded"] = tipo_encoder.fit_transform(X["Tipo"], y) 

        X["Transmision_encoded"] = X["Transmisión"].map({"Mecánico": 0, "Automático": 1})

        X.drop(columns=["marca", "Transmisión", "Tipo"], inplace=True)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        mlflow.set_tracking_uri("http://mlflow:5000")  # Adaptar si usás otro host: sin airflow, era localhost:5000
        mlflow.set_experiment("entrenamiento_orquestado")

        modelos = {
            "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
            "CatBoost": CatBoostRegressor(verbose=0, random_seed=42),
            "SVR": SVR()
        }

        best_score = float("inf")
        best_model_uri = None
        best_name = "mejor_modelo_orquestado"
        client = MlflowClient()

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

        # Registrar el mejor modelo
        result = mlflow.register_model(model_uri=best_model_uri, name=best_name)

        # Cambiar fases
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

    entrenar_y_promover()

dag = train_and_promote_models()
