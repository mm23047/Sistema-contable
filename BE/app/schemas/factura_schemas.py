from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class FacturaCreate(BaseModel):
    cliente: str
    monto_total: float


class FacturaOut(BaseModel):
    id_factura: UUID
    numero_factura: str
    cliente: str
    monto_total: float
    fecha_emision: Optional[datetime] = None
    id_transaccion: int

    class Config:
        orm_mode = True
