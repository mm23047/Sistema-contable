"""
Esquemas Pydantic para Asientos Contables.
Define la validación de datos y serialización para requests y responses de la API.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal

class AsientoBase(BaseModel):
    id_transaccion: int = Field(..., description="ID de la transacción asociada")
    id_cuenta: int = Field(..., description="ID de la cuenta asociada")
    debe: Decimal = Field(default=Decimal("0.00"), ge=0, description="Monto del débito")
    haber: Decimal = Field(default=Decimal("0.00"), ge=0, description="Monto del crédito")
    
    @validator('haber')
    def validate_debe_haber(cls, v, values):
        """Asegurar que exactamente uno de debe o haber sea mayor que 0"""
        debe = values.get('debe', Decimal("0.00"))
        if (debe > 0 and v > 0) or (debe == 0 and v == 0):
            raise ValueError('Exactamente uno de debe o haber debe ser mayor que 0')
        return v

class AsientoCreate(AsientoBase):
    pass

class AsientoUpdate(BaseModel):
    id_transaccion: Optional[int] = None
    id_cuenta: Optional[int] = None
    debe: Optional[Decimal] = Field(None, ge=0)
    haber: Optional[Decimal] = Field(None, ge=0)

class AsientoRead(AsientoBase):
    id_asiento: int
    
    class Config:
        from_attributes = True