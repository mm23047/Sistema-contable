"""
Modelo de Cliente para el sistema de facturación.
Tabla normalizada de clientes reutilizables.
"""
from sqlalchemy import Column, String, Integer, TIMESTAMP, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from BE.app.db import Base


class Cliente(Base):
    __tablename__ = "clientes"
    __table_args__ = {'extend_existing': True}

    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    
    # Información básica
    nombre = Column(String(150), nullable=False, index=True)
    nit = Column(String(20), nullable=True, unique=True, index=True)
    
    # Contacto
    direccion = Column(String(255), nullable=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    
    # Información adicional
    tipo_cliente = Column(String(50), nullable=True, default="INDIVIDUAL")  # INDIVIDUAL, EMPRESA
    notas = Column(Text, nullable=True)
    
    # Auditoría
    fecha_registro = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    activo = Column(String(10), nullable=False, default="SI")  # SI, NO
    
    # Relaciones
    facturas = relationship("Factura", back_populates="cliente_obj")
