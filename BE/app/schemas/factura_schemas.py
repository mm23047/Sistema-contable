from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from decimal import Decimal
import re


class FacturaCreate(BaseModel):
    """Schema para crear una factura nueva (soporta versión legacy y normalizada)"""
    # Cliente (nuevo - normalizado)
    id_cliente: Optional[int] = Field(None, description="ID del cliente (tabla clientes)")
    
    # Cliente legacy (compatibilidad hacia atrás)
    cliente: Optional[str] = Field(None, min_length=1, max_length=150, description="Nombre del cliente (legacy)")
    nit_cliente: Optional[str] = Field(None, max_length=20, description="NIT o RFC del cliente (legacy)")
    direccion_cliente: Optional[str] = Field(None, max_length=255, description="Dirección del cliente")
    telefono_cliente: Optional[str] = Field(None, max_length=20, description="Teléfono del cliente")
    email_cliente: Optional[str] = Field(None, max_length=100, description="Email del cliente")
    
    # Producto o Servicio (legacy para facturas simples)
    producto_servicio: Optional[str] = Field(None, min_length=1, description="Descripción del producto o servicio (legacy)")
    
    @field_validator('email_cliente')
    @classmethod
    def validar_email(cls, v):
        """Validar formato de email solo si se proporciona"""
        if v and v.strip():  # Solo validar si no está vacío
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Debe ser un email válido (ejemplo: usuario@dominio.com)')
        return v if v and v.strip() else None  # Convertir strings vacíos a None
    
    # Montos (opcionales si se proporcionan detalles)
    subtotal: Optional[Decimal] = Field(None, ge=0, description="Subtotal antes de impuestos y descuentos")
    descuento: Optional[Decimal] = Field(0.00, ge=0, description="Descuento aplicado")
    iva: Optional[Decimal] = Field(None, ge=0, description="IVA (13% típicamente)")
    monto_total: Optional[Decimal] = Field(None, gt=0, description="Total de la factura")
    
    # Información adicional
    notas: Optional[str] = Field(None, description="Notas o comentarios de la factura")
    condiciones_pago: Optional[str] = Field("Contado", max_length=100, description="Condiciones de pago")
    vendedor: Optional[str] = Field(None, max_length=100, description="Nombre del vendedor")
    fecha_vencimiento: Optional[datetime] = Field(None, description="Fecha de vencimiento")


class FacturaUpdate(BaseModel):
    """Schema para actualizar una factura (campos opcionales)"""
    cliente: Optional[str] = Field(None, min_length=1, max_length=150)
    nit_cliente: Optional[str] = Field(None, max_length=20)
    direccion_cliente: Optional[str] = Field(None, max_length=255)
    telefono_cliente: Optional[str] = Field(None, max_length=20)
    email_cliente: Optional[str] = Field(None, max_length=100)
    notas: Optional[str] = None
    condiciones_pago: Optional[str] = Field(None, max_length=100)
    vendedor: Optional[str] = Field(None, max_length=100)


class FacturaOut(BaseModel):
    """Schema de respuesta de factura"""
    id_factura: UUID
    numero_factura: str
    
    # Cliente (opcional para compatibilidad con modelo normalizado)
    cliente: Optional[str] = None
    nit_cliente: Optional[str] = None
    direccion_cliente: Optional[str] = None
    telefono_cliente: Optional[str] = None
    email_cliente: Optional[str] = None
    
    # Cliente normalizado
    id_cliente: Optional[int] = None
    
    # Producto o Servicio (opcional, deprecado en favor de detalles)
    producto_servicio: Optional[str] = None
    
    # Montos
    subtotal: Decimal
    descuento: Decimal
    iva: Decimal
    monto_total: Decimal
    
    # Información adicional
    notas: Optional[str] = None
    condiciones_pago: Optional[str] = None
    vendedor: Optional[str] = None
    
    # Fechas
    fecha_emision: datetime
    fecha_vencimiento: Optional[datetime] = None
    
    # Relaciones (opcional)
    id_transaccion: Optional[int] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat() if v else None
        }


class FacturaResumen(BaseModel):
    """Schema resumido de factura para listados"""
    id_factura: UUID
    numero_factura: str
    cliente: str
    monto_total: Decimal
    fecha_emision: datetime
    estado: str = "Generada"
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat() if v else None
        }


# =========================================================
# 🆕 SCHEMAS PARA FACTURAS CON DETALLES (NORMALIZADA)
# =========================================================

class DetalleFacturaItem(BaseModel):
    """Schema para un ítem de detalle de factura"""
    id_producto: int = Field(..., description="ID del producto/servicio")
    cantidad: Decimal = Field(..., gt=0, description="Cantidad del producto")
    precio_unitario: Optional[Decimal] = Field(None, description="Precio unitario (si es diferente al del catálogo)")
    descuento_porcentaje: Optional[Decimal] = Field(0, ge=0, le=100, description="Descuento en porcentaje")
    descuento_monto: Optional[Decimal] = Field(0, ge=0, description="Descuento en monto fijo")


class FacturaConDetallesCreate(BaseModel):
    """Schema para crear factura con múltiples líneas de productos"""
    # Datos de la factura principal
    id_cliente: int = Field(..., description="ID del cliente")
    condiciones_pago: Optional[str] = Field("Contado", max_length=100)
    vendedor: Optional[str] = Field(None, max_length=100)
    fecha_vencimiento: Optional[datetime] = None
    notas: Optional[str] = None
    descuento_global: Optional[Decimal] = Field(0, ge=0, description="Descuento adicional global")
    
    # Líneas de detalle
    detalles: List[DetalleFacturaItem] = Field(..., min_length=1, description="Líneas de productos/servicios")
    
    @field_validator('detalles')
    @classmethod
    def validar_detalles(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Debe incluir al menos un producto/servicio')
        return v

