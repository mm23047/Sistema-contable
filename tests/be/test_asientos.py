"""
Unit tests for Asientos (Journal Entries) functionality.
Tests the creation, validation, and business logic for journal entries.
"""
import os
os.environ["TESTING"] = "true"  # Debe estar ANTES de importar app

import pytest
from fastapi.testclient import TestClient
from BE.app.main import app
from BE.app.db import Base, engine
from BE.app.models.transaccion import Transaccion
from BE.app.models.catalogo_cuentas import CatalogoCuentas
from BE.app.db import SessionLocal
from datetime import datetime

@pytest.fixture
def test_client():
    """Crear cliente de prueba y configurar datos de prueba"""
    Base.metadata.create_all(bind=engine)
    
    # Crear datos de prueba
    db = SessionLocal()
    try:
        # Crear cuenta de prueba
        test_account = CatalogoCuentas(
            codigo_cuenta="1001",
            nombre_cuenta="Caja",
            tipo_cuenta="Activo"
        )
        db.add(test_account)
        db.commit()
        db.refresh(test_account)
        
        # Create test transaction
        test_transaction = Transaccion(
            fecha_transaccion=datetime(2025, 8, 1, 10, 0, 0),
            descripcion="Test transaction",
            tipo="INGRESO",
            categoria="VENTA",
            moneda="USD",
            usuario_creacion="test_user"
        )
        db.add(test_transaction)
        db.commit()
        db.refresh(test_transaction)
        
    finally:
        db.close()
    
    with TestClient(app) as client:
        yield client
    
    Base.metadata.drop_all(bind=engine)

def test_create_asiento_success(test_client):
    """Prueba de creación exitosa de asiento contable"""
    asiento_data = {
        "id_transaccion": 1,
        "id_cuenta": 1,
        "debe": 100.00,
        "haber": 0.00
    }
    
    response = test_client.post("/api/asientos/", json=asiento_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "id_asiento" in data
    assert isinstance(data["id_asiento"], int)

def test_create_asiento_invalid_transaction(test_client):
    """Prueba de creación de asiento contable con transacción inexistente"""
    asiento_data = {
        "id_transaccion": 999,  # Non-existent transaction
        "id_cuenta": 1,
        "debe": 100.00,
        "haber": 0.00
    }
    
    response = test_client.post("/api/asientos/", json=asiento_data)
    
    assert response.status_code == 400
    assert "Transacción no encontrada" in response.text or "Transaction not found" in response.text

def test_create_asiento_invalid_account(test_client):
    """Prueba de creación de asiento contable con cuenta inexistente"""
    asiento_data = {
        "id_transaccion": 1,
        "id_cuenta": 999,  # Non-existent account
        "debe": 100.00,
        "haber": 0.00
    }
    
    response = test_client.post("/api/asientos/", json=asiento_data)
    
    assert response.status_code == 400
    assert "Cuenta no encontrada" in response.text or "Account not found" in response.text

def test_create_asiento_both_debe_haber(test_client):
    """Prueba de creación de asiento contable con debe y haber > 0 (inválido)"""
    asiento_data = {
        "id_transaccion": 1,
        "id_cuenta": 1,
        "debe": 100.00,
        "haber": 50.00  # Both debe and haber > 0 (invalid)
    }
    
    response = test_client.post("/api/asientos/", json=asiento_data)
    
    assert response.status_code == 422  # Pydantic validation error

def test_create_asiento_neither_debe_haber(test_client):
    """Prueba de creación de asiento contable con debe y haber = 0 (inválido)"""
    asiento_data = {
        "id_transaccion": 1,
        "id_cuenta": 1,
        "debe": 0.00,
        "haber": 0.00  # Both debe and haber = 0 (invalid)
    }
    
    response = test_client.post("/api/asientos/", json=asiento_data)
    
    assert response.status_code == 422  # Pydantic validation error

def test_create_asiento_credit_only(test_client):
    """Prueba de creación exitosa de asiento contable solo con haber"""
    asiento_data = {
        "id_transaccion": 1,
        "id_cuenta": 1,
        "debe": 0.00,
        "haber": 100.00
    }
    
    response = test_client.post("/api/asientos/", json=asiento_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "id_asiento" in data

def test_get_asiento_not_found(test_client):
    """Prueba de obtener asiento contable inexistente"""
    response = test_client.get("/api/asientos/999")
    
    assert response.status_code == 404

def test_list_asientos_by_transaction(test_client):
    """Prueba de listar asientos contables filtrados por transacción"""
    # Create an asiento first
    asiento_data = {
        "id_transaccion": 1,
        "id_cuenta": 1,
        "debe": 100.00,
        "haber": 0.00
    }
    test_client.post("/api/asientos/", json=asiento_data)
    
    # List asientos for the transaction
    response = test_client.get("/api/asientos/", params={"id_transaccion": 1})
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id_transaccion"] == 1

# NOTA: Pruebas adicionales a implementar:
# - Probar actualizaciones de asientos con validación
# - Probar eliminación de asientos
# - Probar filtrado por cuenta
# - Probar múltiples asientos para la misma transacción
# - Probar validación de balance entre múltiples asientos
# - Probar montos negativos (deben fallar)
# - Probar manejo de precisión decimal
