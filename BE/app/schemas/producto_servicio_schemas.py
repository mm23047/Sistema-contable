"""
Schemas Pydantic para Producto/Servicio
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from decimal import Decimal


class ProductoServicioCreate(BaseModel):
    """Schema para crear un producto o servicio"""
    codigo: Optional[str] = Field(None, max_length=50, description="Código SKU")
    nombre: str = Field(..., min_length=1, max_length=150, description="Nombre del producto/servicio")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")
    tipo: str = Field("PRODUCTO", description="PRODUCTO o SERVICIO")
    categoria: Optional[str] = Field(None, max_length=100, description="Categoría")
    precio_unitario: Decimal = Field(..., ge=0, description="Precio unitario")
    precio_costo: Optional[Decimal] = Field(0.00, ge=0, description="Costo unitario")
    unidad_medida: str = Field("UNIDAD", max_length=20, description="Unidad de medida")
    stock_actual: Optional[Decimal] = Field(0.00, ge=0, description="Stock actual")
    stock_minimo: Optional[Decimal] = Field(0.00, ge=0, description="Stock mínimo")
    aplica_iva: str = Field("SI", description="SI o NO")
    
    @field_validator('tipo')
    @classmethod
    def validar_tipo(cls, v):
        if v not in ['PRODUCTO', 'SERVICIO']:
            raise ValueError('Tipo debe ser PRODUCTO o SERVICIO')
        return v
    
    @field_validator('aplica_iva')
    @classmethod
    def validar_aplica_iva(cls, v):
        if v not in ['SI', 'NO']:
            raise ValueError('aplica_iva debe ser SI o NO')
        return v


class ProductoServicioUpdate(BaseModel):
    """Schema para actualizar un producto/servicio"""
    codigo: Optional[str] = Field(None, max_length=50)
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    categoria: Optional[str] = Field(None, max_length=100)
    precio_unitario: Optional[Decimal] = Field(None, ge=0)
    precio_costo: Optional[Decimal] = Field(None, ge=0)
    unidad_medida: Optional[str] = Field(None, max_length=20)
    stock_actual: Optional[Decimal] = Field(None, ge=0)
    stock_minimo: Optional[Decimal] = Field(None, ge=0)
    aplica_iva: Optional[str] = None
    activo: Optional[str] = Field(None, description="SI o NO")


class ProductoServicioOut(BaseModel):
    """Schema de respuesta de producto/servicio"""
    id_producto: int
    codigo: Optional[str] = None
    nombre: str
    descripcion: Optional[str] = None
    tipo: str
    categoria: Optional[str] = None
    precio_unitario: Decimal
    precio_costo: Optional[Decimal] = None
    unidad_medida: str
    stock_actual: Optional[Decimal] = None
    stock_minimo: Optional[Decimal] = None
    aplica_iva: str
    activo: str
    fecha_registro: datetime
    
    class Config:
        from_attributes = True


class ProductoServicioResumen(BaseModel):
    """Schema resumido para listados"""
    id_producto: int
    codigo: Optional[str] = None
    nombre: str
    tipo: str
    precio_unitario: Decimal
    stock_actual: Optional[Decimal] = None
    activo: str
    
    class Config:
        from_attributes = True
