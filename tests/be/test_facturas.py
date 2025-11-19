"""
Pruebas unitarias para el módulo de Facturas (API).
Prueba endpoints de creación de facturas con detalles y cálculos.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BE.app.main import app
from BE.app.db import get_db, Base
from datetime import datetime, timedelta

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
def client():
    """Crear cliente de pruebas"""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def setup_data(client):
    """Crear datos de prueba (cliente y productos)"""
    # Crear cliente
    cliente_data = {
        "nombre": "Cliente Test Factura",
        "tipo_cliente": "INDIVIDUAL",
        "nit": "0614-050190-101-7",
        "email": "factura@example.com",
        "activo": True
    }
    cliente_response = client.post("/api/clientes/", json=cliente_data)
    cliente_id = cliente_response.json()["id_cliente"]
    
    # Crear productos
    producto1_data = {
        "codigo": "FACT-PROD-001",
        "nombre": "Producto Factura 1",
        "tipo": "PRODUCTO",
        "precio_venta": 50.00,
        "precio_costo": 30.00,
        "stock_actual": 100,
        "aplica_iva": True,
        "activo": True
    }
    producto1_response = client.post("/api/productos/", json=producto1_data)
    producto1_id = producto1_response.json()["id_producto"]
    
    producto2_data = {
        "codigo": "FACT-PROD-002",
        "nombre": "Producto Factura 2",
        "tipo": "PRODUCTO",
        "precio_venta": 75.00,
        "precio_costo": 50.00,
        "stock_actual": 50,
        "aplica_iva": True,
        "activo": True
    }
    producto2_response = client.post("/api/productos/", json=producto2_data)
    producto2_id = producto2_response.json()["id_producto"]
    
    return {
        "cliente_id": cliente_id,
        "producto1_id": producto1_id,
        "producto2_id": producto2_id
    }

def test_crear_factura_basica(client, setup_data):
    """Probar creación de factura básica sin detalles"""
    fecha_emision = datetime.now().isoformat()
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    factura_data = {
        "numero_factura": "FACT-2025-0001",
        "id_cliente": setup_data["cliente_id"],
        "fecha_emision": fecha_emision,
        "fecha_vencimiento": fecha_vencimiento,
        "subtotal": 100.00,
        "descuento": 0.00,
        "iva": 13.00,
        "total": 113.00,
        "condiciones_pago": "Contado",
        "estado": "PENDIENTE"
    }
    
    response = client.post("/api/facturas/", json=factura_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["numero_factura"] == "FACT-2025-0001"
    assert data["id_cliente"] == setup_data["cliente_id"]
    assert float(data["total"]) == 113.00

def test_crear_factura_con_detalles(client, setup_data):
    """Probar creación de factura completa con líneas de detalle"""
    fecha_emision = datetime.now().isoformat()
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    factura_data = {
        "factura": {
            "numero_factura": "FACT-2025-0002",
            "id_cliente": setup_data["cliente_id"],
            "fecha_emision": fecha_emision,
            "fecha_vencimiento": fecha_vencimiento,
            "subtotal": 175.00,
            "descuento": 0.00,
            "iva": 22.75,
            "total": 197.75,
            "condiciones_pago": "Crédito 30 días",
            "estado": "PENDIENTE"
        },
        "detalles": [
            {
                "id_producto": setup_data["producto1_id"],
                "cantidad": 2,
                "precio_unitario": 50.00,
                "descuento": 0.00,
                "subtotal": 100.00,
                "iva": 13.00,
                "total": 113.00
            },
            {
                "id_producto": setup_data["producto2_id"],
                "cantidad": 1,
                "precio_unitario": 75.00,
                "descuento": 0.00,
                "subtotal": 75.00,
                "iva": 9.75,
                "total": 84.75
            }
        ]
    }
    
    response = client.post("/api/facturas/con-detalles", json=factura_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["numero_factura"] == "FACT-2025-0002"
    assert float(data["total"]) == 197.75

def test_crear_factura_con_descuento(client, setup_data):
    """Probar creación de factura con descuento"""
    fecha_emision = datetime.now().isoformat()
    fecha_vencimiento = (datetime.now() + timedelta(days=15)).isoformat()
    
    subtotal = 100.00
    descuento = 10.00  # 10% de descuento
    subtotal_con_descuento = subtotal - descuento
    iva = subtotal_con_descuento * 0.13
    total = subtotal_con_descuento + iva
    
    factura_data = {
        "numero_factura": "FACT-2025-0003",
        "id_cliente": setup_data["cliente_id"],
        "fecha_emision": fecha_emision,
        "fecha_vencimiento": fecha_vencimiento,
        "subtotal": subtotal,
        "descuento": descuento,
        "iva": iva,
        "total": total,
        "condiciones_pago": "Contado",
        "estado": "PENDIENTE"
    }
    
    response = client.post("/api/facturas/", json=factura_data)
    
    assert response.status_code == 201
    data = response.json()
    assert float(data["descuento"]) == 10.00
    assert float(data["total"]) == pytest.approx(101.70, 0.01)  # 90 + 11.70 IVA

def test_listar_facturas(client, setup_data):
    """Probar listado de facturas"""
    fecha_emision = datetime.now().isoformat()
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    # Crear dos facturas
    for i in range(2):
        factura_data = {
            "numero_factura": f"FACT-2025-000{i+10}",
            "id_cliente": setup_data["cliente_id"],
            "fecha_emision": fecha_emision,
            "fecha_vencimiento": fecha_vencimiento,
            "subtotal": 100.00,
            "descuento": 0.00,
            "iva": 13.00,
            "total": 113.00,
            "condiciones_pago": "Contado",
            "estado": "PENDIENTE"
        }
        client.post("/api/facturas/", json=factura_data)
    
    # Listar
    response = client.get("/api/facturas/")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_obtener_factura_por_id(client, setup_data):
    """Probar obtención de factura por ID"""
    fecha_emision = datetime.now().isoformat()
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    # Crear factura
    factura_data = {
        "numero_factura": "FACT-2025-9999",
        "id_cliente": setup_data["cliente_id"],
        "fecha_emision": fecha_emision,
        "fecha_vencimiento": fecha_vencimiento,
        "subtotal": 150.00,
        "descuento": 0.00,
        "iva": 19.50,
        "total": 169.50,
        "condiciones_pago": "Contado",
        "estado": "PENDIENTE"
    }
    
    create_response = client.post("/api/facturas/", json=factura_data)
    factura_id = create_response.json()["id_factura"]
    
    # Obtener por ID
    response = client.get(f"/api/facturas/{factura_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id_factura"] == factura_id
    assert data["numero_factura"] == "FACT-2025-9999"

def test_actualizar_estado_factura(client, setup_data):
    """Probar actualización del estado de factura"""
    fecha_emision = datetime.now().isoformat()
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    # Crear factura
    factura_data = {
        "numero_factura": "FACT-2025-8888",
        "id_cliente": setup_data["cliente_id"],
        "fecha_emision": fecha_emision,
        "fecha_vencimiento": fecha_vencimiento,
        "subtotal": 100.00,
        "descuento": 0.00,
        "iva": 13.00,
        "total": 113.00,
        "condiciones_pago": "Contado",
        "estado": "PENDIENTE"
    }
    
    create_response = client.post("/api/facturas/", json=factura_data)
    factura_id = create_response.json()["id_factura"]
    
    # Actualizar estado
    update_data = {"estado": "PAGADA"}
    response = client.put(f"/api/facturas/{factura_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "PAGADA"

def test_factura_multiples_productos_con_iva_mixto(client, setup_data):
    """Probar factura con productos que aplican y no aplican IVA"""
    # Crear producto sin IVA
    producto_sin_iva_data = {
        "codigo": "NO-IVA-001",
        "nombre": "Producto Sin IVA",
        "tipo": "PRODUCTO",
        "precio_venta": 100.00,
        "precio_costo": 60.00,
        "stock_actual": 50,
        "aplica_iva": False,
        "activo": True
    }
    producto_sin_iva_response = client.post("/api/productos/", json=producto_sin_iva_data)
    producto_sin_iva_id = producto_sin_iva_response.json()["id_producto"]
    
    fecha_emision = datetime.now().isoformat()
    fecha_vencimiento = (datetime.now() + timedelta(days=30)).isoformat()
    
    # Factura con producto con IVA y sin IVA
    factura_data = {
        "factura": {
            "numero_factura": "FACT-2025-MIX",
            "id_cliente": setup_data["cliente_id"],
            "fecha_emision": fecha_emision,
            "fecha_vencimiento": fecha_vencimiento,
            "subtotal": 150.00,  # 50 (con IVA) + 100 (sin IVA)
            "descuento": 0.00,
            "iva": 6.50,  # Solo del producto con IVA: 50 * 0.13
            "total": 156.50,
            "condiciones_pago": "Contado",
            "estado": "PENDIENTE"
        },
        "detalles": [
            {
                "id_producto": setup_data["producto1_id"],
                "cantidad": 1,
                "precio_unitario": 50.00,
                "descuento": 0.00,
                "subtotal": 50.00,
                "iva": 6.50,
                "total": 56.50
            },
            {
                "id_producto": producto_sin_iva_id,
                "cantidad": 1,
                "precio_unitario": 100.00,
                "descuento": 0.00,
                "subtotal": 100.00,
                "iva": 0.00,
                "total": 100.00
            }
        ]
    }
    
    response = client.post("/api/facturas/con-detalles", json=factura_data)
    
    assert response.status_code == 201
    data = response.json()
    assert float(data["iva"]) == pytest.approx(6.50, 0.01)
    assert float(data["total"]) == pytest.approx(156.50, 0.01)
