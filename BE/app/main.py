"""
Aplicación principal FastAPI para el sistema contable.
Configura la API, middleware y rutas.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from BE.app.routes import catalogo_cuentas, transacciones, asientos, reportes, periodos, factura_routes,libro_mayor
from BE.app.db import create_tables
import os

# Inicializar aplicación FastAPI
app = FastAPI(
    title="Sistema Contable API",
    description="API para sistema de contabilidad con transacciones y asientos",
    version="1.0.0",
)

# Configurar CORS - Permite todos los orígenes para desarrollo
# TODO: Configurar orígenes específicos para producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de la API
app.include_router(catalogo_cuentas.router)
app.include_router(transacciones.router)
app.include_router(asientos.router)
app.include_router(reportes.router)
app.include_router(periodos.router)
app.include_router(factura_routes.router)
app.include_router(libro_mayor.router)

@app.on_event("startup")
def startup_event():
    """Inicializar tablas de la base de datos al arrancar"""
    create_tables()

@app.get("/")
def read_root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Sistema Contable API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "catalogo_cuentas": "/api/catalogo-cuentas",
            "transacciones": "/api/transacciones", 
            "asientos": "/api/asientos",
            "reportes": "/api/reportes",
            "periodos": "/api/periodos",
            "facturas": "/api/facturas",
            "libro_mayor": "/api/libro_mayor"
        }
    }

@app.get("/health")
def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "healthy"}

# Para ejecutar en desarrollo local:
# Leer PORT_BE desde .env usando python-dotenv
# uvicorn app.main:app --host 0.0.0.0 --port ${PORT_BE} --reload

# En producción, el Dockerfile especificará el comando CMD
# TODO: Usar gunicorn/uvicorn workers en producción para mejor rendimiento