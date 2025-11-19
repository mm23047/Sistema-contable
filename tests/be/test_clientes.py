"""
Pruebas unitarias para el módulo de Clientes (API).
Prueba endpoints CRUD de clientes.
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

def test_crear_cliente_individual(test_client):
    """Probar creación de cliente individual"""
    cliente_data = {
        "nombre": "Juan Pérez",
        "tipo_cliente": "INDIVIDUAL",
        "nit": "0614-050190-101-7",
        "email": "juan.perez@example.com",
        "telefono": "+503 7777-8888",
        "direccion": "San Salvador, El Salvador",
        "activo": True
    }
    
    response = test_client.post("/api/clientes/", json=cliente_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Juan Pérez"
    assert data["tipo_cliente"] == "INDIVIDUAL"
    assert data["nit"] == "0614-050190-101-7"
    assert data["activo"] == True

def test_crear_cliente_empresa(test_client):
    """Probar creación de cliente empresa"""
    cliente_data = {
        "nombre": "Tech Solutions S.A. de C.V.",
        "tipo_cliente": "EMPRESA",
        "nit": "0614-120190-102-3",
        "email": "info@techsolutions.com",
        "telefono": "+503 2222-3333",
        "direccion": "Santa Tecla, El Salvador",
        "activo": True
    }
    
    response = test_client.post("/api/clientes/", json=cliente_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Tech Solutions S.A. de C.V."
    assert data["tipo_cliente"] == "EMPRESA"

def test_listar_clientes(test_client):
    """Probar listado de clientes"""
    # Crear dos clientes
    cliente1 = {
        "nombre": "Cliente 1",
        "tipo_cliente": "INDIVIDUAL",
        "nit": "0614-050190-101-7",
        "email": "cliente1@example.com",
        "activo": True
    }
    cliente2 = {
        "nombre": "Cliente 2",
        "tipo_cliente": "EMPRESA",
        "nit": "0614-120190-102-3",
        "email": "cliente2@example.com",
        "activo": True
    }
    
    test_client.post("/api/clientes/", json=cliente1)
    test_client.post("/api/clientes/", json=cliente2)
    
    # Listar
    response = test_client.get("/api/clientes/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_obtener_cliente_por_id(test_client):
    """Probar obtención de cliente por ID"""
    # Crear cliente
    cliente_data = {
        "nombre": "Test Cliente",
        "tipo_cliente": "INDIVIDUAL",
        "nit": "0614-050190-101-7",
        "email": "test@example.com",
        "activo": True
    }
    
    create_response = test_client.post("/api/clientes/", json=cliente_data)
    cliente_id = create_response.json()["id_cliente"]
    
    # Obtener por ID
    response = test_client.get(f"/api/clientes/{cliente_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id_cliente"] == cliente_id
    assert data["nombre"] == "Test Cliente"

def test_actualizar_cliente(test_client):
    """Probar actualización de cliente"""
    # Crear cliente
    cliente_data = {
        "nombre": "Cliente Original",
        "tipo_cliente": "INDIVIDUAL",
        "nit": "0614-050190-101-7",
        "email": "original@example.com",
        "activo": True
    }
    
    create_response = test_client.post("/api/clientes/", json=cliente_data)
    cliente_id = create_response.json()["id_cliente"]
    
    # Actualizar
    update_data = {
        "nombre": "Cliente Actualizado",
        "email": "actualizado@example.com"
    }
    
    response = test_client.put(f"/api/clientes/{cliente_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Cliente Actualizado"
    assert data["email"] == "actualizado@example.com"

def test_desactivar_cliente(test_client):
    """Probar desactivación de cliente (soft delete)"""
    # Crear cliente
    cliente_data = {
        "nombre": "Cliente Activo",
        "tipo_cliente": "INDIVIDUAL",
        "nit": "0614-050190-101-7",
        "activo": True
    }
    
    create_response = test_client.post("/api/clientes/", json=cliente_data)
    cliente_id = create_response.json()["id_cliente"]
    
    # Desactivar
    update_data = {"activo": False}
    response = test_client.put(f"/api/clientes/{cliente_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["activo"] == False

def test_buscar_cliente_por_nit(test_client):
    """Probar búsqueda de cliente por NIT"""
    # Crear cliente
    nit_buscar = "0614-050190-101-7"
    cliente_data = {
        "nombre": "Cliente NIT",
        "tipo_cliente": "INDIVIDUAL",
        "nit": nit_buscar,
        "email": "nit@example.com",
        "activo": True
    }
    
    test_client.post("/api/clientes/", json=cliente_data)
    
    # Buscar por NIT
    response = test_client.get(f"/api/clientes/buscar/nit/{nit_buscar}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["nit"] == nit_buscar
