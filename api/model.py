import mlflow.pyfunc
import pandas as pd
import os

import joblib

ENCODER_PATH = "/opt/airflow/dags/data/processed/encoders/"
marca_encoder = joblib.load(os.path.join(ENCODER_PATH, "marca_encoder.pkl"))
tipo_encoder = joblib.load(os.path.join(ENCODER_PATH, "tipo_encoder.pkl"))


def load_production_model(model_name="mejor_modelo_orquestado", stage="Production"):
    model_uri = f"models:/{model_name}/{stage}"
    model = mlflow.pyfunc.load_model(model_uri=model_uri)
    return model

def preprocess_input(car_data: dict) -> pd.DataFrame:
    df = pd.DataFrame([car_data])

    df["marca_encoded"] = marca_encoder.transform(df["model"])
    df["tipo_encoded"] = tipo_encoder.transform(df["tipo"])
    df["Transmision_encoded"] = df["transmision"].map({"Mecánico": 0, "Automático": 1})

    df["year"] = df["year"]
    df["km"] = df["km"]
    df["motor"] = df["motor"]
    df["puertas"] = df["puertas"]

    # Filtrar y reordenar columnas igual que en el modelo
    df = df[["year", "km", "motor", "puertas", "marca_encoded", "tipo_encoded", "Transmision_encoded"]]  #
    
    return df
