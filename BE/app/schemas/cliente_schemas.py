"""
Schemas Pydantic para Cliente
"""
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re


class ClienteCreate(BaseModel):
    """Schema para crear un cliente nuevo"""
    nombre: str = Field(..., min_length=1, max_length=150, description="Nombre del cliente")
    nit: Optional[str] = Field(None, max_length=20, description="NIT o identificación fiscal")
    direccion: Optional[str] = Field(None, max_length=255, description="Dirección")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono")
    email: Optional[str] = Field(None, max_length=100, description="Email")
    tipo_cliente: str = Field("INDIVIDUAL", description="Tipo: INDIVIDUAL o EMPRESA")
    notas: Optional[str] = Field(None, description="Notas adicionales")
    
    @field_validator('email')
    @classmethod
    def validar_email(cls, v):
        """Validar formato de email solo si se proporciona"""
        if v and v.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v):
                raise ValueError('Debe ser un email válido')
        return v if v and v.strip() else None
    
    @field_validator('tipo_cliente')
    @classmethod
    def validar_tipo(cls, v):
        if v not in ['INDIVIDUAL', 'EMPRESA']:
            raise ValueError('Tipo debe ser INDIVIDUAL o EMPRESA')
        return v


class ClienteUpdate(BaseModel):
    """Schema para actualizar un cliente"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    nit: Optional[str] = Field(None, max_length=20)
    direccion: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    tipo_cliente: Optional[str] = None
    notas: Optional[str] = None
    activo: Optional[str] = Field(None, description="SI o NO")


class ClienteOut(BaseModel):
    """Schema de respuesta de cliente"""
    id_cliente: int
    nombre: str
    nit: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    tipo_cliente: str
    notas: Optional[str] = None
    fecha_registro: datetime
    activo: str
    
    class Config:
        from_attributes = True


class ClienteResumen(BaseModel):
    """Schema resumido para listados"""
    id_cliente: int
    nombre: str
    nit: Optional[str] = None
    tipo_cliente: str
    activo: str
    
    class Config:
        from_attributes = True
