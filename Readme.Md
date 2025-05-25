# 🚗 Predicción de Precios de Autos Usados con Airflow y MLflow

Este proyecto implementa un flujo de trabajo completo de Machine Learning enfocado en la predicción del precio de autos usados en Bolivia. La solución automatiza desde el scrapping de datos hasta el despliegue del mejor modelo en producción utilizando Apache Airflow como orquestador y MLflow para el tracking y versionado de modelos.

## 🧠 Objetivo del Proyecto

1. **Scrapear** datos de autos usados desde una plataforma online.
2. **Limpiar** los datos descargados de forma incremental.
3. **Preprocesar** variables categóricas, valores faltantes y construir los datasets `X_train`, `y_train`.
4. **Entrenar** tres modelos de regresión y promover el mejor a producción.
5. **Realizar predicciones** con el modelo en producción.

## 🧰 Tecnologías utilizadas

| Herramienta         | Descripción                                           |
|---------------------|-------------------------------------------------------|
| **Apache Airflow**  | Orquestador de tareas para flujos de trabajo diarios |
| **MLflow**          | Seguimiento, versionado y registro de modelos ML     |
| **Docker Compose**  | Entorno reproducible con contenedores                |
| **Pandas & Scikit-learn** | Procesamiento de datos y entrenamiento de modelos |
| **CatBoost / SVR**  | Modelos adicionales para comparación de desempeño    |

## ⚙️ Estructura del Proyecto
├── airflow/
│ ├── dags/
│ │ └── entrenamiento_modelos_regresion_dag.py
│ ├── plugins/
│ ├── config/
│ └── secrets/
├── dockerfiles/
│ └── airflow/ # Imagen extendida con dependencias
├── mlruns/ # Volumen persistente de MLflow
├── data/
│ └── processed/ # Archivos .pkl listos para entrenamiento
├── docker-compose.yaml
├── requirements.txt
└── README.md


## 🧪 Flujo de trabajo orquestado

### DAG diario en Airflow (`entrenamiento_modelos_regresion`):

1. **Carga del dataset** desde un archivo `.pkl` previamente limpiado.
2. **Preprocesamiento**:
   - Encoding de variables categóricas (`TargetEncoder` para marca, tipo, etc.).
   - Imputación o mapeo de variables binarias (`Transmisión`).
3. **Entrenamiento de modelos**:
   - `RandomForestRegressor`
   - `CatBoostRegressor`
   - `SVR`
4. **Evaluación con MAE** y registro de métricas en MLflow.
5. **Promoción automática** del mejor modelo al stage "Production".
6. **Transición del modelo anterior a "Staging"** si existe.

## 🔁 Ejecución

### 1. Clonar el repositorio
```bash
git clone --llenar--
cd --llenar--
```
# 2. Crear y dar permisos a los volúmenes
```bash
mkdir -p mlruns
sudo chown -R 50000:0 mlruns
```

# 3. Levantar el entorno completo
```bash
docker-compose up --build -d
```
Para detenerlo:
```Bash
docker compose down
```

Para detenerlo y eliminar todo:
```Bash
docker compose down --rmi all --volumes
```

# 44. Acceder a interfaces
Airflow UI: http://localhost:8080

MLflow UI: http://localhost:5000


```Bash
docker compose up
```

### Para editar desde VSC: sudo chown -R federico:federico /home/federico/Proyectos/CEIA/MLops1/
### Si da error de escritura sobre el path: sudo chown -R 50000:0 ./mlruns
