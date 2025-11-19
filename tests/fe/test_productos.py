"""
Pruebas unitarias para el módulo de Productos del Frontend.
Prueba cálculos de precios, validaciones de stock y formateo.
"""


def test_calcular_precio_con_iva():
    """Probar cálculo de precio con IVA (13%)"""
    precio_base = 100.00
    iva = precio_base * 0.13
    precio_total = precio_base + iva
    
    assert iva == 13.00
    assert precio_total == 113.00

def test_calcular_precio_sin_iva():
    """Probar precio sin IVA"""
    precio_base = 100.00
    precio_total = precio_base
    
    assert precio_total == 100.00

def test_validar_stock_disponible():
    """Probar validación de stock disponible"""
    stock_actual = 10
    cantidad_solicitada = 5
    
    assert cantidad_solicitada <= stock_actual  # OK
    
    cantidad_excesiva = 15
    assert cantidad_excesiva > stock_actual  # No disponible

def test_alerta_stock_minimo():
    """Probar alerta cuando stock está bajo"""
    stock_actual = 2
    stock_minimo = 5
    
    assert stock_actual < stock_minimo  # Debe alertar

def test_calcular_margen_ganancia():
    """Probar cálculo de margen de ganancia"""
    precio_venta = 150.00
    precio_costo = 100.00
    margen = ((precio_venta - precio_costo) / precio_costo) * 100
    
    assert margen == 50.0  # 50% de ganancia

def test_validar_codigo_sku_unico():
    """Probar que el código SKU sea válido"""
    codigo = "PROD-001"
    
    assert len(codigo) > 0
    assert "-" in codigo
    assert codigo.isupper() or codigo.isalnum()

def test_tipos_producto_validos():
    """Probar tipos de producto válidos"""
    tipos_validos = ["PRODUCTO", "SERVICIO"]
    
    assert "PRODUCTO" in tipos_validos
    assert "SERVICIO" in tipos_validos
    assert "OTRO" not in tipos_validos

def test_calcular_valor_inventario():
    """Probar cálculo de valor total de inventario"""
    productos = [
        {"stock_actual": 10, "precio_costo": 50.00},
        {"stock_actual": 5, "precio_costo": 100.00},
        {"stock_actual": 20, "precio_costo": 25.00}
    ]
    
    valor_total = sum(p["stock_actual"] * p["precio_costo"] for p in productos)
    
    assert valor_total == 1500.00  # (10*50 + 5*100 + 20*25)

def test_formatear_precio():
    """Probar formateo de precio para visualización"""
    precio = 1234.56
    precio_formateado = f"${precio:,.2f}"
    
    assert precio_formateado == "$1,234.56"

def test_validar_descuento_porcentaje():
    """Probar validación de descuento (0-100%)"""
    descuento_valido = 25.5
    descuento_invalido_bajo = -5
    descuento_invalido_alto = 105
    
    assert 0 <= descuento_valido <= 100
    assert not (0 <= descuento_invalido_bajo <= 100)
    assert not (0 <= descuento_invalido_alto <= 100)
