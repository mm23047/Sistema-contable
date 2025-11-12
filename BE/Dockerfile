# Dockerfile del Backend para Sistema Contable
FROM python:3.11-slim

# Optimizaciones para construcción más rápida
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONPATH=/

# Establecer directorio de trabajo
WORKDIR /BE

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Exponer puerto desde variable de entorno
ENV PORT_BE=8000
# EXPOSE $PORT_BE

# Comando para ejecutar la aplicación
CMD ["python", "-m", "uvicorn", "BE.app.main:app", "--host", "0.0.0.0", "--port", "8000"]