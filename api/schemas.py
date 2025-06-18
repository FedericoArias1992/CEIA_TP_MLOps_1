"""
schemas.py

Esquemas de entrada y salida para la API de predicción de precios de autos usados,
definidos con Pydantic. Incluye validaciones, enumeraciones restringidas
y un ejemplo integrado para documentación Swagger.

"""
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


# Enumeraciones para restringir entrada
class TipoEnum(str, Enum):
    """
    Tipos de autos admitidos.
    """
    SUV = "SUV"
    Hatchback = "Hatchback"
    Sedan = "Sedán"
    CityCar = "CityCar"
    Camioneta = "Camioneta"
    Furgon = "Furgón"

class ModelEnum(str, Enum):
    """
    Modelos de autos reconocidos por el modelo entrenado.
    """
    Nissan_Murano = "Nissan Murano"
    Mitsubishi_Montero = "Mitsubishi Montero"
    Renault_Koleos = "Renault Koleos"
    Toyota_Rush = "Toyota Rush"
    Suzuki_Dzire_Sedan = "Suzuki Dzire Sedan"
    New_Pathfinder = "New Pathfinder"
    Suzuki_S_cross = "Suzuki S-cross"
    Celerio = "Celerio"
    S2 = "S2"
    Alto = "Alto"
    Nissan_Frontier = "Nissan Frontier"
    Suzuki_Celerio = "Suzuki Celerio"
    Nissan_March = "Nissan March"
    Cs_55 = "Cs-55"
    Grand_Vitara = "Grand Vitara"
    Cs35 = "Cs35"
    Nissan_Sentra = "Nissan Sentra"
    Honda_Ridgeline = "Honda Ridgeline"
    Hyundai_Galloper = "Hyundai Galloper"
    Mazda_Cx_5 = "Mazda Cx-5"
    Expedition = "Expedition"
    Toyota_Tacoma = "Toyota Tacoma"
    Wrangler = "Wrangler"
    Mercedes_Benz_GLK = "Mercedes Benz GLK"
    Sportage = "Sportage"
    Nissan_Urvan = "Nissan Urvan"
    Ecosport = "Ecosport"
    Changan_Cs35 = "Changan Cs35"
    Caio_Millenium_III = "Caio Millenium III"
    Tracker = "Tracker"
    Suzuki_Alto = "Suzuki Alto"
    Ford_Explorer = "Ford Explorer"
    Suzuki_S_presso = "Suzuki S-presso"
    Benz_E = "Benz E"
    Ssangyong_XLV = "Ssangyong XLV"
    KIA_Sportage = "KIA Sportage"
    JAC_J6 = "JAC J6"
    Mazda_Cx_3 = "Mazda Cx-3"
    JAC_T8 = "JAC T8"
    Jeep_Compass = "Jeep Compass"
    Sonet = "Sonet"
    N300_Max = "N300 Max"
    KIA_Carens = "KIA Carens"
    Toyota_Starlet = "Toyota Starlet"
    Hyundai_I_10 = "Hyundai I-10"
    Suzuki_APV = "Suzuki APV"
    Toyota_Agya = "Toyota Agya"
    Peugeot_301 = "Peugeot 301"
    Mitsubishi_Outlander = "Mitsubishi Outlander"
    Chevrolet_Tracker = "Chevrolet Tracker"
    Renault_Sandero = "Renault Sandero"
    Nissan_Rogue = "Nissan Rogue"
    Num_523 = "523"
    Nissan_X_trail = "Nissan X-trail"
    ASX = "ASX"
    Montero = "Montero"

class TransmisionEnum(str, Enum):
    """
    Tipos de transmisión admitidos por el modelo.
    """
    automatico = "Automático"
    mecanico = "Mecánico"

class CarInput(BaseModel):
    """
    Modelo de entrada para predicción.

    Contiene todas las variables necesarias para estimar el precio
    de un vehículo usado en Bolivia.
    """

    year: int = Field(..., ge=1980, le=2025, description="Año del vehículo")
    km: int = Field(..., ge=0, le=1000000, description="Kilómetros recorridos")
    model: ModelEnum = Field(..., description="Modelo del vehículo")
    tipo: TipoEnum = Field(..., description="Tipo de carrocería, por ejemplo: SUV, Sedán, Hatchback")
    motor: float = Field(..., ge=0.5, le=8.0, description="Tamaño del motor en litros")
    transmision: TransmisionEnum = Field(..., description="Tipo de transmisión del Automático o Mecánico")
    puertas: int = Field(..., ge=2, le=5, description="Cantidad de puertas")

    class Config:
        schema_extra = {
            "example": {
                "year": 2025,
                "km": 1000,
                "model": "Alto",
                "tipo": "SUV",
                "motor": 1200,
                "transmision": "Automático",
                "puertas": 2
            }
        }

class PredictionOutput(BaseModel):
    """
    Modelo de salida para la predicción.

    Representa el valor estimado del vehículo en la moneda local.
    """

    predicted_price: float
