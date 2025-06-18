"""
app.py

Aplicación web desarrollada con Streamlit para la predicción del precio de autos usados en Bolivia.

La interfaz permite al usuario ingresar datos relevantes del vehículo y consumir un endpoint FastAPI
para obtener el precio estimado, utilizando el modelo cargado en producción.
"""
import streamlit as st
import requests

# Configuración de la página
st.set_page_config(page_title="Predicción de precio de autos", layout="centered")

st.title("🚗 Predicción de Precio de Autos Usados")

# Listas de opciones (esto debería venir del backend idealmente)
MODELOS = [
    "Nissan Murano", "Mitsubishi Montero", "Renault Koleos", "Toyota Rush", "Suzuki Dzire Sedan", "New Pathfinder",
    "Suzuki S-cross", "Celerio", "S2", "Alto", "Nissan Frontier", "Suzuki Celerio", "Nissan March", "Cs-55",
    "Grand Vitara", "Cs35", "Nissan Sentra", "Honda Ridgeline", "Hyundai Galloper", "Mazda Cx-5", "Expedition",
    "Toyota Tacoma", "Wrangler", "Mercedes Benz GLK", "Sportage", "Nissan Urvan", "Ecosport", "Changan Cs35",
    "Caio Millenium III", "Tracker", "Suzuki Alto", "Ford Explorer", "Suzuki S-presso", "Benz E", "Ssangyong XLV",
    "KIA Sportage", "JAC J6", "Mazda Cx-3", "JAC T8", "Jeep Compass", "Sonet", "N300 Max", "KIA Carens",
    "Toyota Starlet", "Hyundai I-10", "Suzuki APV", "Toyota Agya", "Peugeot 301", "Mitsubishi Outlander",
    "Chevrolet Tracker", "Renault Sandero", "Nissan Rogue", "523", "Nissan X-trail", "ASX", "Montero"
]

TIPOS = ["SUV", "Hatchback", "Sedán", "CityCar", "Camioneta", "Furgón"]

TRANSMISIONES = ["Automático", "Mecánico"]

# Formulario
with st.form(key="form_auto"):
    year = st.number_input("Año del vehículo", min_value=1980, max_value=2025, value=2020)
    km = st.number_input("Kilómetros recorridos", min_value=0, max_value=1_000_000, value=50000, step=1000)
    model = st.selectbox("Modelo del vehículo", MODELOS)
    tipo = st.selectbox("Tipo de carrocería", TIPOS)
    motor = st.number_input("Tamaño del motor (litros)", min_value=0.5, max_value=8.0, value=1.6, step=0.1)
    transmision = st.selectbox("Transmisión", TRANSMISIONES)
    puertas = st.slider("Cantidad de puertas", min_value=2, max_value=5, value=4)

    submit = st.form_submit_button("Predecir")

# Acción al enviar
if submit:
    input_data = {
        "year": int(year),
        "km": int(km),
        "model": model,
        "tipo": tipo,
        "motor": float(motor),
        "transmision": transmision,
        "puertas": int(puertas),
    }

    try:
        # Cambiar el host si no estás en localhost
        response = requests.post("http://fastapi-ml:8000/predict", json=input_data)
        if response.status_code == 200:
            prediction = response.json()
            st.success(f"💰 Precio estimado: **{prediction['predicted_price']:.2f} USD**")
        else:
            st.error("❌ Error al predecir. Verifica los datos ingresados.")
            st.json(response.json())
    except Exception as e:
        st.error(f"🚨 No se pudo conectar con la API: {e}")
