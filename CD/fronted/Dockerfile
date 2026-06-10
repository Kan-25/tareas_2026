
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema que Reflex necesita para compilar
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instalar Reflex e httpx
RUN pip install --no-cache-dir reflex httpx

# Copiar todo el contenido de la carpeta fronted al contenedor
COPY . .

# Exponer el puerto de la app (3000) y el puerto de eventos de Reflex (8001)
EXPOSE 3000 8001

# Ejecutar Reflex configurando el puerto backend propio en el 8001 para que no choque con tu FastAPI
CMD ["reflex", "run", "--frontend-port", "3000", "--backend-port", "8001"]