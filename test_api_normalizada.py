# Script de Pruebas - API Normalizada
# Validar endpoints de clientes, productos y facturas

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Imprime respuesta formateada"""
    print(f"\n{'='*60}")
    print(f"🔹 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)

# =========================================================
# TEST 1: CLIENTES
# =========================================================

print("\n🧪 PRUEBAS DE CLIENTES")

# 1.1 Listar clientes
print("\n1. Listar clientes existentes")
resp = requests.get(f"{BASE_URL}/api/clientes/")
print_response("GET /api/clientes/", resp)

# 1.2 Crear cliente individual
print("\n2. Crear cliente individual")
nuevo_cliente = {
    "nombre": "Juan Carlos Martínez",
    "nit": "0614-050190-101-7",
    "contacto_nombre": "Juan Carlos Martínez",
    "contacto_telefono": "+503 7777-8888",
    "contacto_email": "jcmartinez@gmail.com",
    "direccion": "San Salvador, Colonia Escalón",
    "tipo_cliente": "INDIVIDUAL",
    "activo": "SI"
}
resp = requests.post(f"{BASE_URL}/api/clientes/", json=nuevo_cliente)
print_response("POST /api/clientes/ (Individual)", resp)
cliente_id_1 = resp.json().get("id_cliente") if resp.status_code == 201 else None

# 1.3 Crear cliente empresa
print("\n3. Crear cliente empresa")
cliente_empresa = {
    "nombre": "SOLUCIONES TECNOLÓGICAS S.A. DE C.V.",
    "nit": "0614-120190-102-3",
    "contacto_nombre": "Ana García",
    "contacto_telefono": "+503 2222-3333",
    "contacto_email": "ventas@soltec.com.sv",
    "direccion": "Santa Tecla, Centro Comercial La Joya",
    "tipo_cliente": "EMPRESA",
    "activo": "SI"
}
resp = requests.post(f"{BASE_URL}/api/clientes/", json=cliente_empresa)
print_response("POST /api/clientes/ (Empresa)", resp)
cliente_id_2 = resp.json().get("id_cliente") if resp.status_code == 201 else None

# 1.4 Buscar por NIT
print("\n4. Buscar cliente por NIT")
resp = requests.get(f"{BASE_URL}/api/clientes/buscar/nit/0614-120190-102-3")
print_response("GET /api/clientes/buscar/nit/{nit}", resp)

# 1.5 Estadísticas
print("\n5. Estadísticas de clientes")
resp = requests.get(f"{BASE_URL}/api/clientes/estadisticas/resumen")
print_response("GET /api/clientes/estadisticas/resumen", resp)

# =========================================================
# TEST 2: PRODUCTOS
# =========================================================

print("\n\n🧪 PRUEBAS DE PRODUCTOS")

# 2.1 Listar productos
print("\n1. Listar productos existentes")
resp = requests.get(f"{BASE_URL}/api/productos/")
print_response("GET /api/productos/", resp)

# 2.2 Crear producto
print("\n2. Crear producto nuevo")
nuevo_producto = {
    "codigo": "SERV-WEB-001",
    "nombre": "Desarrollo Web Corporativo",
    "tipo": "SERVICIO",
    "categoria": "Desarrollo de Software",
    "descripcion": "Sitio web corporativo con CMS, responsive design, 5 páginas",
    "precio_unitario": 1500.00,
    "precio_costo": 800.00,
    "stock_actual": 0,
    "stock_minimo": 0,
    "aplica_iva": "SI",
    "activo": "SI"
}
resp = requests.post(f"{BASE_URL}/api/productos/", json=nuevo_producto)
print_response("POST /api/productos/ (Servicio)", resp)
producto_id_servicio = resp.json().get("id_producto") if resp.status_code == 201 else None

# 2.3 Crear producto físico
print("\n3. Crear producto físico con stock")
producto_fisico = {
    "codigo": "IMPL-EPSON-L3250",
    "nombre": "Impresora Multifuncional Epson L3250",
    "tipo": "PRODUCTO",
    "categoria": "Periféricos",
    "descripcion": "Impresora de inyección de tinta, sistema continuo, WiFi",
    "precio_unitario": 285.00,
    "precio_costo": 210.00,
    "stock_actual": 12,
    "stock_minimo": 3,
    "aplica_iva": "SI",
    "activo": "SI"
}
resp = requests.post(f"{BASE_URL}/api/productos/", json=producto_fisico)
print_response("POST /api/productos/ (Producto Físico)", resp)
producto_id_fisico = resp.json().get("id_producto") if resp.status_code == 201 else None

# 2.4 Buscar por código
print("\n4. Buscar producto por código")
resp = requests.get(f"{BASE_URL}/api/productos/buscar/codigo/LAP-HP-001")
print_response("GET /api/productos/buscar/codigo/{codigo}", resp)
producto_laptop_id = resp.json().get("id_producto") if resp.status_code == 200 else None

# 2.5 Ajustar stock (entrada)
if producto_id_fisico:
    print(f"\n5. Ajustar stock (entrada de 5 unidades)")
    resp = requests.patch(f"{BASE_URL}/api/productos/{producto_id_fisico}/stock?cantidad=5")
    print_response(f"PATCH /api/productos/{producto_id_fisico}/stock?cantidad=5", resp)

# 2.6 Productos bajo stock
print("\n6. Productos con stock bajo")
resp = requests.get(f"{BASE_URL}/api/productos/alertas/bajo-stock")
print_response("GET /api/productos/alertas/bajo-stock", resp)

# 2.7 Estadísticas
print("\n7. Estadísticas de productos")
resp = requests.get(f"{BASE_URL}/api/productos/estadisticas/resumen")
print_response("GET /api/productos/estadisticas/resumen", resp)

# =========================================================
# TEST 3: FACTURAS CON DETALLES
# =========================================================

print("\n\n🧪 PRUEBAS DE FACTURAS CON DETALLES")

# 3.1 Crear factura con múltiples productos
if cliente_id_1 and producto_laptop_id and producto_id_servicio:
    print("\n1. Crear factura multi-producto")
    
    factura_con_detalles = {
        "id_cliente": cliente_id_1,
        "condiciones_pago": "Crédito 30 días",
        "vendedor": "Carlos López",
        "notas": "Cliente corporativo - Descuento por volumen",
        "descuento_global": 100.00,
        "detalles": [
            {
                "id_producto": producto_laptop_id,
                "cantidad": 3,
                "descuento_porcentaje": 5
            },
            {
                "id_producto": producto_id_servicio,
                "cantidad": 1,
                "descuento_porcentaje": 0
            }
        ]
    }
    
    resp = requests.post(f"{BASE_URL}/api/facturas/con-detalles", json=factura_con_detalles)
    print_response("POST /api/facturas/con-detalles", resp)
    factura_id = resp.json().get("id_factura") if resp.status_code == 201 else None
    
    # 3.2 Obtener factura creada
    if factura_id:
        print(f"\n2. Obtener factura creada")
        resp = requests.get(f"{BASE_URL}/api/facturas/{factura_id}")
        print_response(f"GET /api/facturas/{factura_id}", resp)
else:
    print("\n⚠️ No se pueden crear facturas - faltan IDs de clientes o productos")

# 3.3 Listar facturas
print("\n3. Listar todas las facturas")
resp = requests.get(f"{BASE_URL}/api/facturas/")
print_response("GET /api/facturas/", resp)

# 3.4 Estadísticas de facturación
print("\n4. Estadísticas de facturación")
resp = requests.get(f"{BASE_URL}/api/facturas/estadisticas")
print_response("GET /api/facturas/estadisticas", resp)

# 3.5 Top clientes
print("\n5. Top clientes por compras")
resp = requests.get(f"{BASE_URL}/api/facturas/top-clientes?limite=5")
print_response("GET /api/facturas/top-clientes", resp)

# =========================================================
# TEST 4: VALIDACIONES
# =========================================================

print("\n\n🧪 PRUEBAS DE VALIDACIONES")

# 4.1 Intentar crear cliente con NIT duplicado
print("\n1. Validar NIT duplicado (debe fallar)")
cliente_duplicado = {
    "nombre": "Otro Cliente",
    "nit": "0614-120190-102-3",  # NIT ya existente
    "tipo_cliente": "INDIVIDUAL",
    "activo": "SI"
}
resp = requests.post(f"{BASE_URL}/api/clientes/", json=cliente_duplicado)
print_response("POST /api/clientes/ (NIT duplicado)", resp)

# 4.2 Intentar stock negativo
if producto_id_fisico:
    print("\n2. Validar stock negativo (debe fallar)")
    resp = requests.patch(f"{BASE_URL}/api/productos/{producto_id_fisico}/stock?cantidad=-1000")
    print_response(f"PATCH /api/productos/{producto_id_fisico}/stock (negativo)", resp)

# 4.3 Intentar factura sin detalles
if cliente_id_1:
    print("\n3. Validar factura sin detalles (debe fallar)")
    factura_sin_detalles = {
        "id_cliente": cliente_id_1,
        "detalles": []
    }
    resp = requests.post(f"{BASE_URL}/api/facturas/con-detalles", json=factura_sin_detalles)
    print_response("POST /api/facturas/con-detalles (sin detalles)", resp)

print("\n\n✅ PRUEBAS COMPLETADAS")
print("="*60)
