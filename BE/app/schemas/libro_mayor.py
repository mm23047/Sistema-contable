"""
Esquemas Pydantic para el Libro Mayor.
Define la estructura de datos para requests y responses del libro mayor.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from typing import List, Optional
from datetime import date
from decimal import Decimal

class SubcuentaResponse(BaseModel):
    """Esquema para una subcuenta en el libro mayor"""
    codigo_cuenta: str = Field(..., min_length=1, max_length=20, description="Código de la subcuenta")
    nombre_cuenta: str = Field(..., min_length=1, max_length=100, description="Nombre de la subcuenta")
    tipo_cuenta: str = Field(..., description="Tipo de cuenta (Activo, Pasivo, Capital, Ingreso, Egreso)")
    total_debe: Decimal = Field(..., ge=0, description="Total de débitos")
    total_haber: Decimal = Field(..., ge=0, description="Total de créditos")
    saldo: Decimal = Field(..., description="Saldo de la subcuenta (debe - haber, puede ser negativo)")
    
    @field_validator('tipo_cuenta')
    @classmethod
    def validate_tipo_cuenta(cls, v: str) -> str:
        tipos_validos = {'Activo', 'Pasivo', 'Capital', 'Ingreso', 'Egreso'}
        if v not in tipos_validos:
            raise ValueError(f'Tipo de cuenta debe ser uno de: {tipos_validos}')
        return v

class CuentaMayorResponse(BaseModel):
    """Esquema para una cuenta mayor en el libro mayor"""
    codigo_mayor: str = Field(..., min_length=1, max_length=10, description="Código de la cuenta mayor")
    nombre_mayor: str = Field(..., min_length=1, max_length=100, description="Nombre de la cuenta mayor")
    total_debe: Decimal = Field(..., ge=0, description="Total de débitos agregado")
    total_haber: Decimal = Field(..., ge=0, description="Total de créditos agregado")
    saldo: Decimal = Field(..., description="Saldo agregado de la cuenta mayor (puede ser negativo)")
    subcuentas: List[SubcuentaResponse] = Field(default=[], description="Lista de subcuentas (si se solicita detalle)")

class ResumenLibroMayor(BaseModel):
    """Esquema para el resumen del libro mayor"""
    total_cuentas: int = Field(..., ge=0, description="Número total de cuentas mayores")
    total_debe_general: Decimal = Field(..., ge=0, description="Suma total de débitos")
    total_haber_general: Decimal = Field(..., ge=0, description="Suma total de créditos")
    diferencia: Decimal = Field(..., ge=0, description="Diferencia absoluta entre debe y haber")
    fecha_generacion: str = Field(..., description="Fecha de generación del reporte en formato ISO")
    
    @field_validator('fecha_generacion')
    @classmethod
    def validate_fecha_iso(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('La fecha debe estar en formato ISO (YYYY-MM-DD)')

class FiltrosAplicados(BaseModel):
    """Esquema para los filtros aplicados en la consulta"""
    digitos: int = Field(..., ge=1, le=10, description="Número de dígitos usado para agrupar")
    fecha_inicio: Optional[str] = Field(None, description="Fecha inicio en formato ISO")
    fecha_fin: Optional[str] = Field(None, description="Fecha fin en formato ISO")
    incluir_detalle: bool = Field(..., description="Si se incluyó detalle de subcuentas")
    
    @field_validator('fecha_inicio', 'fecha_fin')
    @classmethod
    def validate_fechas_iso(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                date.fromisoformat(v)
                return v
            except ValueError:
                raise ValueError('Las fechas deben estar en formato ISO (YYYY-MM-DD)')
        return v

class LibroMayorResponse(BaseModel):
    """Esquema completo de respuesta del libro mayor"""
    mayores: List[CuentaMayorResponse] = Field(..., description="Lista de cuentas mayores")
    resumen: ResumenLibroMayor = Field(..., description="Resumen estadístico")
    filtros_aplicados: FiltrosAplicados = Field(..., description="Filtros aplicados en la consulta")
    
    model_config = ConfigDict(
        # Convertir Decimal a float para JSON
        json_encoders={Decimal: float},
        # Permitir uso de atributos de ORM
        from_attributes=True,
        # Documentación adicional
        json_schema_extra={
            "example": {
                "mayores": [
                    {
                        "codigo_mayor": "1100",
                        "nombre_mayor": "Caja y Bancos",
                        "total_debe": 15000.00,
                        "total_haber": 5000.00,
                        "saldo": 10000.00,
                        "subcuentas": []
                    }
                ],
                "resumen": {
                    "total_cuentas": 5,
                    "total_debe_general": 50000.00,
                    "total_haber_general": 45000.00,
                    "diferencia": 5000.00,
                    "fecha_generacion": "2025-11-15"
                },
                "filtros_aplicados": {
                    "digitos": 4,
                    "fecha_inicio": None,
                    "fecha_fin": None,
                    "incluir_detalle": False
                }
            }
        }
    )

class LibroMayorRequest(BaseModel):
    """Esquema para solicitar el libro mayor"""
    digitos: int = Field(4, ge=1, le=10, description="Número de dígitos para agrupar cuentas mayores")
    fecha_inicio: Optional[date] = Field(None, description="Fecha de inicio para filtrar")
    fecha_fin: Optional[date] = Field(None, description="Fecha fin para filtrar")
    incluir_detalle: bool = Field(False, description="Incluir subcuentas en el detalle")
    
    @model_validator(mode='after')
    def validate_rango_fechas(self):
        if self.fecha_fin is not None and self.fecha_inicio is not None:
            if self.fecha_fin < self.fecha_inicio:
                raise ValueError('La fecha fin no puede ser anterior a la fecha inicio')
        return self
    
    @field_validator('fecha_inicio', 'fecha_fin')
    @classmethod
    def validate_fechas_no_futuras(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError('Las fechas no pueden ser futuras')
        return v
    
    model_config = ConfigDict(
        json_encoders={date: lambda v: v.isoformat()},
        json_schema_extra={
            "example": {
                "digitos": 4,
                "fecha_inicio": "2025-01-01",
                "fecha_fin": "2025-11-15",
                "incluir_detalle": True
            }
        }
    )