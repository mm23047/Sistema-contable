"""
Pruebas unitarias para el módulo de Productos (API).
Prueba endpoints CRUD de productos, cálculos de precios e inventario.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BE.app.main import app
from BE.app.db import get_db, Base

# Configuración de base de datos de pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def test_client():
    """Crear cliente de pruebas"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)

def test_crear_producto(test_client):
    """Probar creación de producto"""
    producto_data = {
        "codigo": "PROD-001",
        "nombre": "Camiseta Polo",
        "descripcion": "Camiseta tipo polo de algodón",
        "tipo": "PRODUCTO",
        "precio_unitario": 25.00,
        "precio_costo": 15.00,
        "stock_actual": 50,
        "stock_minimo": 10,
        "aplica_iva": "SI",
        "activo": "SI"
    }
    
    response = test_client.post("/api/productos/", json=producto_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["codigo"] == "PROD-001"
    assert data["nombre"] == "Camiseta Polo"

def test_crear_servicio(test_client):
    """Probar creación de servicio"""
    servicio_data = {
        "codigo": "SERV-001",
        "nombre": "Consultoría Contable",
        "descripcion": "Servicio de consultoría contable por hora",
        "tipo": "SERVICIO",
        "precio_unitario": 50.00,
        "aplica_iva": "SI",
        "activo": "SI"
    }
    
    response = test_client.post("/api/productos/", json=servicio_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["tipo"] == "SERVICIO"

def test_listar_productos(test_client):
    """Probar listado de productos"""
    prod1 = {
        "codigo": "PROD-001",
        "nombre": "Producto 1",
        "tipo": "PRODUCTO",
        "precio_unitario": 10.00,
        "activo": "SI"
    }
    
    test_client.post("/api/productos/", json=prod1)
    
    response = test_client.get("/api/productos/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
