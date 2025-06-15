FROM python:3.8-slim 

WORKDIR /app

COPY ./api /app

RUN pip install --no-cache-dir \
    fastapi uvicorn \
    mlflow==2.17.2 \
    scikit-learn==1.3.2 \
    numpy==1.24.4 \
    scipy==1.10.1 \
    psutil==5.9.7 \
    catboost \
    joblib \
    dill \
    category_encoders

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
