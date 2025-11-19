"""
Schemas Pydantic para Detalle de Factura
"""
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID


class FacturaDetalleCreate(BaseModel):
    """Schema para crear una línea de detalle en la factura"""
    id_producto: int = Field(..., gt=0, description="ID del producto/servicio")
    descripcion: Optional[str] = Field(None, description="Descripción adicional")
    cantidad: Decimal = Field(..., gt=0, description="Cantidad")
    precio_unitario: Decimal = Field(..., ge=0, description="Precio unitario")
    descuento_porcentaje: Optional[Decimal] = Field(0.00, ge=0, le=100, description="Descuento en %")
    descuento_monto: Optional[Decimal] = Field(0.00, ge=0, description="Descuento en monto fijo")


class FacturaDetalleUpdate(BaseModel):
    """Schema para actualizar una línea de detalle"""
    id_producto: Optional[int] = Field(None, gt=0)
    descripcion: Optional[str] = None
    cantidad: Optional[Decimal] = Field(None, gt=0)
    precio_unitario: Optional[Decimal] = Field(None, ge=0)
    descuento_porcentaje: Optional[Decimal] = Field(None, ge=0, le=100)
    descuento_monto: Optional[Decimal] = Field(None, ge=0)


class FacturaDetalleOut(BaseModel):
    """Schema de respuesta de detalle de factura"""
    id_detalle: int
    id_factura: UUID
    id_producto: int
    descripcion: Optional[str] = None
    cantidad: Decimal
    precio_unitario: Decimal
    descuento_porcentaje: Optional[Decimal] = None
    descuento_monto: Optional[Decimal] = None
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    
    # Información del producto (JOIN)
    producto_nombre: Optional[str] = None
    producto_codigo: Optional[str] = None
    
    class Config:
        from_attributes = True
