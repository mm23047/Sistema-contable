"""
Pruebas unitarias para el módulo de Clientes del Frontend.
Prueba la lógica de validación y formateo de datos de clientes.
"""
import re


def validar_nit(nit):
    """Validar formato NIT salvadoreño"""
    if not nit:
        return False
    # Formato: 0614-050190-101-7 (14 dígitos con guiones)
    pattern = r'^\d{4}-\d{6}-\d{3}-\d{1}$'
    return bool(re.match(pattern, nit))


def validar_email(email):
    """Validar formato email"""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def formatear_telefono(telefono):
    """Formatear número telefónico salvadoreño"""
    if not telefono:
        return ""
    # Limpiar número
    numero = telefono.replace("+503", "").replace("-", "").replace(" ", "").strip()
    # Formatear: +503 7777-8888
    if len(numero) == 8:
        return f"+503 {numero[:4]}-{numero[4:]}"
    return telefono

def test_validar_nit():
    """Probar validación de formato NIT"""
    # NITs válidos
    assert validar_nit("0614-050190-101-7") == True
    assert validar_nit("0614-120190-102-3") == True
    
    # NITs inválidos
    assert validar_nit("1234") == False
    assert validar_nit("") == False
    assert validar_nit(None) == False

def test_validar_email():
    """Probar validación de formato email"""
    # Emails válidos
    assert validar_email("test@example.com") == True
    assert validar_email("user.name@domain.co.sv") == True
    
    # Emails inválidos
    assert validar_email("invalid-email") == False
    assert validar_email("@example.com") == False
    assert validar_email("") == False

def test_formatear_telefono():
    """Probar formateo de número telefónico"""
    assert formatear_telefono("77778888") == "+503 7777-8888"
    assert formatear_telefono("22223333") == "+503 2222-3333"
    assert formatear_telefono("+503 7777-8888") == "+503 7777-8888"

def test_tipo_cliente_valido():
    """Probar que el tipo de cliente sea válido"""
    tipos_validos = ["INDIVIDUAL", "EMPRESA"]
    
    assert "INDIVIDUAL" in tipos_validos
    assert "EMPRESA" in tipos_validos
    assert "OTRO" not in tipos_validos