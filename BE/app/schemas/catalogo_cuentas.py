"""
Esquemas Pydantic para Catálogo de Cuentas.
Define la validación de datos y serialización para requests y responses de la API.
"""
from pydantic import BaseModel, Field
from typing import Optional

class CatalogoCuentaBase(BaseModel):
    codigo_cuenta: str = Field(..., min_length=1, max_length=20, description="Código único de cuenta")
    nombre_cuenta: str = Field(..., min_length=1, max_length=100, description="Nombre de la cuenta")
    tipo_cuenta: str = Field(..., pattern="^(Activo|Pasivo|Capital|Ingreso|Egreso)$", description="Tipo de cuenta")

class CatalogoCuentaCreate(CatalogoCuentaBase):
    pass

class CatalogoCuentaUpdate(BaseModel):
    codigo_cuenta: Optional[str] = Field(None, min_length=1, max_length=20)
    nombre_cuenta: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo_cuenta: Optional[str] = Field(None, pattern="^(Activo|Pasivo|Capital|Ingreso|Egreso)$")

class CatalogoCuentaRead(CatalogoCuentaBase):
    id_cuenta: int
    
    class Config:
        from_attributes = True