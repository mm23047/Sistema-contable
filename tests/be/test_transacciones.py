"""
Pruebas unitarias para funcionalidad de Transacciones.
Prueba la creación, validación y lógica de negocio para transacciones.
"""
import os
os.environ["TESTING"] = "true"  # Debe estar ANTES de importar app

import pytest
from fastapi.testclient import TestClient
from BE.app.main import app
from BE.app.db import Base, engine, SessionLocal
from BE.app.models.periodo import PeriodoContable
from datetime import datetime

@pytest.fixture
def test_client():
    """Crear cliente de pruebas"""
    Base.metadata.create_all(bind=engine)
    
    # Crear periodo contable de prueba
    db = SessionLocal()
    try:
        periodo = PeriodoContable(
            fecha_inicio=datetime(2025, 8, 1).date(),
            fecha_fin=datetime(2025, 8, 31).date(),
            tipo_periodo="MENSUAL",
            estado="ABIERTO"
        )
        db.add(periodo)
        db.commit()
    finally:
        db.close()
    
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)

def test_create_transaction_success(test_client):
    """Probar creación exitosa de transacción"""
    transaction_data = {
        "fecha_transaccion": "2025-08-01T10:00:00",
        "descripcion": "Venta de camisetas",
        "tipo": "INGRESO",
        "categoria": "VENTA",
        "moneda": "USD",
        "usuario_creacion": "estudiante1",
        "id_periodo": 1
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