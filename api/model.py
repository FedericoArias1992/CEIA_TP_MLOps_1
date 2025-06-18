"""
model.py

Módulo auxiliar para la API de predicción de precios de autos usados.

Contiene funciones para:
- Cargar el modelo entrenado desde MLflow en stage "Production"
- Aplicar los mismos preprocesamientos que se usaron durante el entrenamiento
  (encoding de variables categóricas y selección de features)
"""

import mlflow.pyfunc
from mlflow.exceptions import RestException
import pandas as pd
import os
import joblib

# Ruta de los encoders preentrenados
ENCODER_PATH = "/opt/airflow/dags/data/processed/encoders/"
_cached_model = None  # Cache en memoria para evitar múltiples cargas


def load_production_model(model_name="mejor_modelo_orquestado", stage="Production"):
    """
    Carga el modelo registrado en MLflow en el stage indicado.
    Si el modelo no existe, devuelve None tal que no se rompa la API.
    """
    model_uri = f"models:/{model_name}/{stage}"
    try:
        model = mlflow.pyfunc.load_model(model_uri=model_uri)
        return model
    except RestException as e:
        print(f"⚠️ Modelo no encontrado en MLflow: {e}")
        return None


def get_cached_model():
    """
    Devuelve el modelo desde cache. Si no está en cache, lo carga una vez.
    """
    global _cached_model
    if _cached_model is None:
        _cached_model = load_production_model()
    return _cached_model


# Cargamos encoders al arrancar
try:
    marca_encoder = joblib.load(os.path.join(ENCODER_PATH, "marca_encoder.pkl"))
    tipo_encoder = joblib.load(os.path.join(ENCODER_PATH, "tipo_encoder.pkl"))
except Exception as e:
    print(f"⚠️ No se pudieron cargar los encoders: {e}")
    marca_encoder = None
    tipo_encoder = None


def preprocess_input(car_data: dict) -> pd.DataFrame:
    """
    Aplica el mismo preprocesamiento que durante el entrenamiento.
    """
    df = pd.DataFrame([car_data])

    # Aplicamos transformaciones
    df["marca_encoded"] = marca_encoder.transform(df["model"]) if marca_encoder else 0
    df["tipo_encoded"] = tipo_encoder.transform(df["tipo"]) if tipo_encoder else 0
    df["Transmision_encoded"] = df["transmision"].map({"Mecánico": 0, "Automático": 1})

    # Seleccionamos columnas usadas por el modelo
    df = df[
        ["year", 
         "km", 
         "motor", 
         "puertas", 
         "marca_encoded", 
         "tipo_encoded", 
         "Transmision_encoded"]]

    return df
