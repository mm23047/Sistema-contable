"""
Pruebas unitarias para el módulo de Facturas (API).
Prueba endpoints de creación de facturas con detalles y cálculos.
"""
import os
os.environ["TESTING"] = "true"  # Debe estar ANTES de importar app

import pytest
from fastapi.testclient import TestClient
from BE.app.main import app
from BE.app.db import Base, engine, SessionLocal
from datetime import datetime, timedelta

@pytest.fixture
def test_client():
    """Crear cliente de pruebas"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def setup_data(test_client):
    """Crear datos de prueba (cliente y productos)"""
    # Crear cliente
    cliente_data = {
        "nombre": "Cliente Test Factura",
        "tipo_cliente": "INDIVIDUAL",
        "nit": "0614-050190-101-7",
        "email": "factura@example.com",
        "activo": "SI"
    }
    cliente_response = test_client.post("/api/clientes", json=cliente_data)
    cliente_id = cliente_response.json()["id_cliente"]
    
    # Crear productos
    producto1_data = {
        "codigo": "FACT-PROD-001",
        "nombre": "Producto Factura 1",
        "descripcion": "Producto para factura",
        "tipo": "PRODUCTO",
        "precio_unitario": 50.00,
        "precio_costo": 30.00,
        "stock_actual": 100,
        "stock_minimo": 10,
        "aplica_iva": "SI",
        "activo": "SI"
    }
    producto1_response = test_client.post("/api/productos", json=producto1_data)
    producto1_id = producto1_response.json()["id_producto"]
    
    producto2_data = {
        "codigo": "FACT-PROD-002",
        "nombre": "Producto Factura 2",
        "descripcion": "Producto para factura",
        "tipo": "PRODUCTO",
        "precio_unitario": 75.00,
        "precio_costo": 50.00,
        "stock_actual": 50,
        "stock_minimo": 10,
        "aplica_iva": "SI",
        "activo": "SI"
    }
    producto2_response = test_client.post("/api/productos", json=producto2_data)
    producto2_id = producto2_response.json()["id_producto"]
    
    return {
        "cliente_id": cliente_id,
        "producto1_id": producto1_id,
        "producto2_id": producto2_id
    }

def test_crear_factura_basica(test_client, setup_data):
    """Probar creación de factura básica sin detalles"""
    fecha_emision = datetime.now().isoformat()
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    factura_data = {
        "id_cliente": setup_data["cliente_id"],
        "fecha_vencimiento": fecha_vencimiento,
        "subtotal": 100.00,
        "descuento": 0.00,
        "iva": 13.00,
        "monto_total": 113.00,
        "condiciones_pago": "Contado"
    }
    
    response = test_client.post("/api/facturas/", json=factura_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "numero_factura" in data
    assert data["id_cliente"] == setup_data["cliente_id"]
    assert float(data["monto_total"]) == 113.00

def test_crear_factura_con_detalles(test_client, setup_data):
    """Probar creación de factura completa con líneas de detalle"""
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    factura_data = {
        "id_cliente": setup_data["cliente_id"],
        "fecha_vencimiento": fecha_vencimiento,
        "condiciones_pago": "Crédito 30 días",
        "descuento_global": 0.00,
        "detalles": [
            {
                "id_producto": setup_data["producto1_id"],
                "cantidad": 2,
                "precio_unitario": 50.00,
                "descuento_monto": 0.00
            },
            {
                "id_producto": setup_data["producto2_id"],
                "cantidad": 1,
                "precio_unitario": 75.00,
                "descuento_monto": 0.00
            }
        ]
    }
    
    response = test_client.post("/api/facturas/con-detalles", json=factura_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "numero_factura" in data
    assert float(data["monto_total"]) == pytest.approx(197.75, 0.01)

def test_crear_factura_con_descuento(test_client, setup_data):
    """Probar creación de factura con descuento"""
    fecha_emision = datetime.now().isoformat()
    fecha_vencimiento = (datetime.now() + timedelta(days=15)).isoformat()
    
    subtotal = 100.00
    descuento = 10.00  # 10% de descuento
    subtotal_con_descuento = subtotal - descuento
    iva = subtotal_con_descuento * 0.13
    total = subtotal_con_descuento + iva
    
    factura_data = {
        "id_cliente": setup_data["cliente_id"],
        "fecha_vencimiento": fecha_vencimiento,
        "subtotal": subtotal,
        "descuento": descuento,
        "iva": iva,
        "monto_total": total,
        "condiciones_pago": "Contado"
    }
    
    response = test_client.post("/api/facturas/", json=factura_data)
    
    assert response.status_code == 201
    data = response.json()
    assert float(data["descuento"]) == 10.00
    assert float(data["monto_total"]) == pytest.approx(101.70, 0.01)  # 90 + 11.70 IVA

def test_listar_facturas(test_client, setup_data):
    """Probar listado de facturas"""
    fecha_emision = datetime.now().isoformat()
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    # Crear dos facturas
    for i in range(2):
        factura_data = {
            "id_cliente": setup_data["cliente_id"],
            "fecha_vencimiento": fecha_vencimiento,
            "subtotal": 100.00,
            "descuento": 0.00,
            "iva": 13.00,
            "monto_total": 113.00,
            "condiciones_pago": "Contado"
        }
        test_client.post("/api/facturas/", json=factura_data)
    
    # Listar
    response = test_client.get("/api/facturas/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_obtener_factura_por_id(test_client, setup_data):
    """Probar obtención de factura por ID"""
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    # Crear factura
    factura_data = {
        "id_cliente": setup_data["cliente_id"],
        "fecha_vencimiento": fecha_vencimiento,
        "subtotal": 150.00,
        "descuento": 0.00,
        "iva": 19.50,
        "monto_total": 169.50,
        "condiciones_pago": "Contado"
    }
    
    create_response = test_client.post("/api/facturas/", json=factura_data)
    create_data = create_response.json()
    factura_id = create_data["id_factura"]
    numero_factura = create_data["numero_factura"]
    
    # Obtener por ID
    response = test_client.get(f"/api/facturas/{factura_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id_factura"] == factura_id
    assert data["numero_factura"] == numero_factura

def test_actualizar_estado_factura(test_client, setup_data):
    """Probar actualización de factura (notas)"""
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    # Crear factura
    factura_data = {
        "id_cliente": setup_data["cliente_id"],
        "fecha_vencimiento": fecha_vencimiento,
        "subtotal": 100.00,
        "descuento": 0.00,
        "iva": 13.00,
        "monto_total": 113.00,
        "condiciones_pago": "Contado",
        "notas": "Factura inicial"
    }
    
    create_response = test_client.post("/api/facturas/", json=factura_data)
    factura_id = create_response.json()["id_factura"]
    
    # Actualizar notas
    update_data = {"notas": "Factura pagada en efectivo"}
    response = test_client.put(f"/api/facturas/{factura_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["notas"] == "Factura pagada en efectivo"

def test_factura_multiples_productos_con_iva_mixto(test_client, setup_data):
    """Probar factura con productos que aplican y no aplican IVA"""
    # Crear producto sin IVA
    producto_sin_iva_data = {
        "codigo": "NO-IVA-001",
        "nombre": "Producto Sin IVA",
        "descripcion": "Producto sin IVA",
        "tipo": "PRODUCTO",
        "precio_unitario": 100.00,
        "precio_costo": 60.00,
        "stock_actual": 50,
        "stock_minimo": 10,
        "aplica_iva": "NO",
        "activo": "SI"
    }
    producto_sin_iva_response = test_client.post("/api/productos", json=producto_sin_iva_data)
    producto_sin_iva_id = producto_sin_iva_response.json()["id_producto"]
    
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    # Factura con producto con IVA y sin IVA
    factura_data = {
        "id_cliente": setup_data["cliente_id"],
        "fecha_vencimiento": fecha_vencimiento,
        "condiciones_pago": "Contado",
        "descuento_global": 0.00,
        "detalles": [
            {
                "id_producto": setup_data["producto1_id"],
                "cantidad": 1,
                "precio_unitario": 50.00,
                "descuento_monto": 0.00
            },
            {
                "id_producto": producto_sin_iva_id,
                "cantidad": 1,
                "precio_unitario": 100.00,
                "descuento_monto": 0.00
            }
        ]
    }
    
    response = test_client.post("/api/facturas/con-detalles", json=factura_data)
    
    assert response.status_code == 201
    data = response.json()
    assert float(data["iva"]) == pytest.approx(6.50, 0.01)
    assert float(data["monto_total"]) == pytest.approx(156.50, 0.01)
