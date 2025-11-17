"""
Modelo SQLAlchemy para Transacciones.
Define la estructura de la tabla de transacciones.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from BE.app.db import Base

class Transaccion(Base):
    __tablename__ = "transacciones"
    __table_args__ = {'extend_existing': True}
    
    id_transaccion = Column(Integer, primary_key=True, autoincrement=True)
    fecha_transaccion = Column(DateTime, nullable=False)
    descripcion = Column(Text, nullable=False)
    tipo = Column(String(10), nullable=False)  # INGRESO, EGRESO
    moneda = Column(String(3), nullable=False, default='USD')
    fecha_creacion = Column(DateTime, nullable=False, default=func.current_timestamp())
    usuario_creacion = Column(String(50), nullable=False)
    id_periodo = Column(Integer, ForeignKey("periodos_contables.id_periodo"))
    categoria = Column(String, nullable=False)
    
    # Relaciones
    periodo = relationship("PeriodoContable", back_populates="transacciones")
    asientos = relationship("Asiento", back_populates="transaccion", cascade="all, delete-orphan")
    
    # TODO: Implementar restricciones CHECK en producción:
    # CHECK (tipo IN ('INGRESO','EGRESO'))
    
    def __repr__(self):
        return f"<Transaccion(id={self.id_transaccion}, tipo='{self.tipo}', fecha='{self.fecha_transaccion}')>"