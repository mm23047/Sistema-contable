"""
Esquemas Pydantic para Períodos Contables.
Define la validación de datos y serialización para requests y responses de la API.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date

class PeriodoBase(BaseModel):
    fecha_inicio: date = Field(..., description="Fecha de inicio del período")
    fecha_fin: date = Field(..., description="Fecha de fin del período")
    tipo_periodo: str = Field(..., pattern="^(MENSUAL|TRIMESTRAL|ANUAL)$", description="Tipo de período")
    estado: str = Field(default="ABIERTO", pattern="^(ABIERTO|CERRADO)$", description="Estado del período")
    
    @validator('fecha_fin')
    def validate_fecha_fin(cls, v, values):
        if 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('fecha_fin debe ser posterior a fecha_inicio')
        return v

class PeriodoCreate(PeriodoBase):
    pass

class PeriodoUpdate(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    tipo_periodo: Optional[str] = Field(None, pattern="^(MENSUAL|TRIMESTRAL|ANUAL)$")
    estado: Optional[str] = Field(None, pattern="^(ABIERTO|CERRADO)$")

class PeriodoRead(PeriodoBase):
    id_periodo: int
    
    class Config:
        from_attributes = True