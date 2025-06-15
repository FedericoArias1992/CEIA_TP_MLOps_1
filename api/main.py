from fastapi import FastAPI
from model import load_production_model, preprocess_input
from schemas import CarInput, PredictionOutput

app = FastAPI(title="Modelo de Predicción de Precios de Autos Usados")

model = load_production_model()

@app.post("/predict", response_model=PredictionOutput)
def predict_price(car: CarInput):
    df = preprocess_input(car.dict())
    prediction = model.predict(df)[0]
    return {"predicted_price": prediction}
