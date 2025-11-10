# Dockerfile del Frontend para Sistema Contable
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Exponer puerto desde variable de entorno
ENV PORT_FE=8501
EXPOSE $PORT_FE

# Comando para ejecutar la aplicación Streamlit
CMD streamlit run app.py --server.port=$PORT_FE --server.address=0.0.0.0