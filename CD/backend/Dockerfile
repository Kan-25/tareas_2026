
FROM python:3.11-slim

WORKDIR /app

# Instalar las librerías necesarias para el backend
RUN pip install --no-cache-dir fastapi uvicorn numpy pydantic

# Copiar el archivo de código al contenedor
COPY main.py .

# Exponer el puerto del backend
EXPOSE 8000

# Comando para iniciar FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]