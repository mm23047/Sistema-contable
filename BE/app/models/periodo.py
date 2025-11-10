"""
Modelo SQLAlchemy para Períodos Contables.
Define la estructura de la tabla de períodos contables.
"""
from sqlalchemy import Column, Integer, String, Date, CheckConstraint
from sqlalchemy.orm import relationship
from app.db import Base

class PeriodoContable(Base):
    __tablename__ = "periodos_contables"
    
    id_periodo = Column(Integer, primary_key=True, autoincrement=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    tipo_periodo = Column(String(20), nullable=False)  # MENSUAL, TRIMESTRAL, ANUAL
    estado = Column(String(10), nullable=False, default='ABIERTO')
    
    # Relaciones
    transacciones = relationship("Transaccion", back_populates="periodo")
    
    # TODO: Implementar restricciones CHECK en producción:
    # CHECK (tipo_periodo IN ('MENSUAL','TRIMESTRAL','ANUAL'))
    # CHECK (fecha_fin > fecha_inicio)
    
    def __repr__(self):
        return f"<PeriodoContable(id={self.id_periodo}, tipo='{self.tipo_periodo}', estado='{self.estado}')>"