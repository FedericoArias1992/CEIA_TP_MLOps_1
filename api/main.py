"""
main.py

API REST desarrollada con FastAPI para exponer un modelo de machine learning que predice
el precio de autos usados en Bolivia.

La API recibe como input las características del vehículo en formato JSON, procesa la entrada,
y devuelve el precio estimado usando el modelo en stage "Production" desde MLflow.
"""

from fastapi import FastAPI, HTTPException
from model import get_cached_model, preprocess_input
from schemas import CarInput, PredictionOutput

app = FastAPI(title="API de Predicción de Precio de Autos Usados")

@app.post("/predict", response_model=PredictionOutput)
def predict_price(car: CarInput):
    """
    Endpoint principal para obtener el precio estimado de un auto.
    Si el modelo no está disponible aún, responde con 503.
    """
    model = get_cached_model()
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo no disponible. Aún no ha sido entrenado o registrado en MLflow, por favor espera a completar el ciclo de descarga-entrenamiento"
        )

    df = preprocess_input(car.dict())
    prediction = model.predict(df)[0]
    return {"predicted_price": prediction}


@app.get("/status")
def check_model_status():
    """
    Revisa si el modelo en producción está disponible.
    Útil para monitoreo externo o UI.
    """
    model = get_cached_model()
    return {"status": "ready" if model else "unavailable"}