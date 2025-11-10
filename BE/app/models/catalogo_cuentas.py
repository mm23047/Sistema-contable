"""
Modelo SQLAlchemy para Catálogo de Cuentas.
Define la estructura de la tabla de catálogo de cuentas.
"""
from sqlalchemy import Column, Integer, String
from app.db import Base

class CatalogoCuentas(Base):
    __tablename__ = "catalogo_cuentas"
    
    id_cuenta = Column(Integer, primary_key=True, autoincrement=True)
    codigo_cuenta = Column(String(20), unique=True, nullable=False, index=True)
    nombre_cuenta = Column(String(100), nullable=False)
    tipo_cuenta = Column(String(50), nullable=False)  # Activo, Pasivo, Capital, Ingreso, Egreso
    
    def __repr__(self):
        return f"<CatalogoCuentas(codigo='{self.codigo_cuenta}', nombre='{self.nombre_cuenta}', tipo='{self.tipo_cuenta}')>"