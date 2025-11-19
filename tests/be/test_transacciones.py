"""
Pruebas unitarias para funcionalidad de Transacciones.
Prueba la creación, validación y lógica de negocio para transacciones.
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

def test_create_transaction_success(test_client):
    """Probar creación exitosa de transacción"""
    transaction_data = {
        "fecha_transaccion": "2025-08-01T10:00:00",
        "descripcion": "Venta de camisetas",
        "tipo": "INGRESO",
        "moneda": "USD",
        "usuario_creacion": "estudiante1"
    }
    
    response = test_client.post("/api/transacciones/", json=transaction_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "id_transaccion" in data
    assert isinstance(data["id_transaccion"], int)

def test_create_transaction_invalid_type(test_client):
    """Prueba de creación de transacción con tipo inválido"""
    transaction_data = {
        "fecha_transaccion": "2025-08-01T10:00:00",
        "descripcion": "Venta de camisetas",
        "tipo": "INVALID_TYPE",  # Invalid type
        "moneda": "USD",
        "usuario_creacion": "estudiante1"
    }
    
    response = test_client.post("/api/transacciones/", json=transaction_data)
    
    assert response.status_code == 422  # Validation error

def test_create_transaction_missing_description(test_client):
    """Prueba de creación de transacción con campo requerido faltante"""
    transaction_data = {
        "fecha_transaccion": "2025-08-01T10:00:00",
        # Missing descripcion
        "tipo": "INGRESO",
        "moneda": "USD",
        "usuario_creacion": "estudiante1"
    }
    
    response = test_client.post("/api/transacciones/", json=transaction_data)
    
    assert response.status_code == 422  # Validation error

def test_get_transaction_not_found(test_client):
    """Prueba de obtener transacción inexistente"""
    response = test_client.get("/api/transacciones/999")
    
    assert response.status_code == 404

def test_list_transactions_empty(test_client):
    """Prueba de listar transacciones cuando no existen"""
    response = test_client.get("/api/transacciones/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

# NOTA: Pruebas adicionales a implementar:
# - Probar actualizaciones de transacciones
# - Probar eliminación de transacciones con política de cascada
# - Probar filtrado de transacciones por fecha, período, tipo
# - Probar validación de período cuando se especifica
# - Probar creación concurrente de transacciones
# - Probar transacción con asientos asociados