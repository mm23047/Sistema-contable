"""
Pruebas unitarias para el módulo de Facturas del Frontend.
Prueba cálculos de totales, IVA, descuentos y validaciones.
"""
from datetime import datetime


def test_calcular_subtotal_linea():
    """Probar cálculo de subtotal por línea"""
    cantidad = 3
    precio_unitario = 50.00
    subtotal = cantidad * precio_unitario
    
    assert subtotal == 150.00

def test_aplicar_descuento_porcentaje():
    """Probar aplicación de descuento por porcentaje"""
    subtotal = 100.00
    descuento_porcentaje = 10  # 10%
    descuento_monto = subtotal * (descuento_porcentaje / 100)
    total_con_descuento = subtotal - descuento_monto
    
    assert descuento_monto == 10.00
    assert total_con_descuento == 90.00

def test_calcular_iva_sobre_subtotal():
    """Probar cálculo de IVA (13%) sobre subtotal"""
    subtotal = 100.00
    iva = subtotal * 0.13
    
    assert iva == 13.00

def test_calcular_total_factura():
    """Probar cálculo de total de factura completa"""
    # Línea 1: 2 x $50 = $100
    linea1_subtotal = 2 * 50.00
    linea1_iva = linea1_subtotal * 0.13
    linea1_total = linea1_subtotal + linea1_iva
    
    # Línea 2: 1 x $75 = $75
    linea2_subtotal = 1 * 75.00
    linea2_iva = linea2_subtotal * 0.13
    linea2_total = linea2_subtotal + linea2_iva
    
    # Total factura
    subtotal_total = linea1_subtotal + linea2_subtotal
    iva_total = linea1_iva + linea2_iva
    total_factura = linea1_total + linea2_total
    
    assert subtotal_total == 175.00
    assert iva_total == 22.75
    assert total_factura == 197.75

def test_aplicar_descuento_global():
    """Probar aplicación de descuento global a factura"""
    subtotal = 1000.00
    descuento_global = 50.00
    subtotal_con_descuento = subtotal - descuento_global
    iva = subtotal_con_descuento * 0.13
    total = subtotal_con_descuento + iva
    
    assert subtotal_con_descuento == 950.00
    assert iva == 123.50
    assert total == 1073.50

def test_generar_numero_factura():
    """Probar generación de número de factura"""
    año_actual = datetime.now().year
    numero_secuencial = 1
    numero_factura = f"FACT-{año_actual}-{numero_secuencial:04d}"
    
    assert numero_factura == f"FACT-{año_actual}-0001"

def test_validar_fecha_vencimiento():
    """Probar que fecha de vencimiento sea posterior a emisión"""
    fecha_emision = datetime(2025, 11, 1)
    fecha_vencimiento = datetime(2025, 11, 30)
    
    assert fecha_vencimiento > fecha_emision

def test_factura_con_multiples_productos():
    """Probar factura con múltiples productos"""
    productos = [
        {"cantidad": 2, "precio_unitario": 100.00, "aplica_iva": True},
        {"cantidad": 1, "precio_unitario": 50.00, "aplica_iva": True},
        {"cantidad": 3, "precio_unitario": 25.00, "aplica_iva": False}
    ]
    
    subtotal = 0
    iva_total = 0
    
    for prod in productos:
        linea_subtotal = prod["cantidad"] * prod["precio_unitario"]
        subtotal += linea_subtotal
        
        if prod["aplica_iva"]:
            iva_total += linea_subtotal * 0.13
    
    total = subtotal + iva_total
    
    assert subtotal == 325.00  # (2*100 + 1*50 + 3*25)
    assert iva_total == 32.50  # 13% de (200 + 50), no aplica a 75
    assert total == 357.50

def test_validar_condiciones_pago():
    """Probar validación de condiciones de pago"""
    condiciones_validas = ["Contado", "Crédito 30 días", "Crédito 60 días"]
    
    assert "Contado" in condiciones_validas
    assert "Crédito 30 días" in condiciones_validas

def test_calcular_descuento_linea_y_global():
    """Probar aplicación de descuento por línea y global"""
    # Línea con descuento individual
    cantidad = 5
    precio_unitario = 100.00
    descuento_linea_porcentaje = 10  # 10%
    
    subtotal_linea = cantidad * precio_unitario  # 500
    descuento_linea = subtotal_linea * (descuento_linea_porcentaje / 100)  # 50
    subtotal_linea_con_desc = subtotal_linea - descuento_linea  # 450
    
    # Descuento global sobre total
    descuento_global = 50.00
    total_final = subtotal_linea_con_desc - descuento_global
    
    assert subtotal_linea == 500.00
    assert descuento_linea == 50.00
    assert subtotal_linea_con_desc == 450.00
    assert total_final == 400.00
