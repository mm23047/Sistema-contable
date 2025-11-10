# Dockerfile del Backend para Sistema Contable
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/

# Exponer puerto desde variable de entorno
ENV PORT_BE=8000
EXPOSE $PORT_BE

# Comando para ejecutar la aplicación
# TODO: usar gunicorn/uvicorn workers en producción
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT_BE