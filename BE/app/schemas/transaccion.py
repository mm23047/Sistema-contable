"""
Esquemas Pydantic para Transacciones.
Define la validación de datos y serialización para requests y responses de la API.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class TransaccionBase(BaseModel):
    fecha_transaccion: datetime = Field(..., description="Fecha y hora de la transacción")
    descripcion: str = Field(..., min_length=1, description="Descripción de la transacción")
    tipo: str = Field(..., pattern="^(INGRESO|EGRESO)$", description="Tipo de transacción")
    moneda: str = Field(default="USD", min_length=3, max_length=3, description="Código de moneda")
    usuario_creacion: str = Field(..., min_length=1, max_length=50, description="Usuario que creó la transacción")
    id_periodo: int = Field(..., description="ID del período contable asociado (requerido)")

class TransaccionCreate(TransaccionBase):
    pass

class TransaccionUpdate(BaseModel):
    fecha_transaccion: Optional[datetime] = None
    descripcion: Optional[str] = Field(None, min_length=1)
    tipo: Optional[str] = Field(None, pattern="^(INGRESO|EGRESO)$")
    moneda: Optional[str] = Field(None, min_length=3, max_length=3)
    usuario_creacion: Optional[str] = Field(None, min_length=1, max_length=50)
    id_periodo: Optional[int] = None

class TransaccionRead(TransaccionBase):
    id_transaccion: int
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True