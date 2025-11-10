"""
Modelo SQLAlchemy para Asientos Contables.
Define la estructura de la tabla de asientos contables.
"""
from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db import Base

class Asiento(Base):
    __tablename__ = "asientos"
    
    id_asiento = Column(Integer, primary_key=True, autoincrement=True)
    id_transaccion = Column(Integer, ForeignKey("transacciones.id_transaccion"), nullable=False)
    id_cuenta = Column(Integer, ForeignKey("catalogo_cuentas.id_cuenta"), nullable=False)
    debe = Column(Numeric(15, 2), nullable=False, default=0.00)
    haber = Column(Numeric(15, 2), nullable=False, default=0.00)
    
    # Relaciones
    transaccion = relationship("Transaccion", back_populates="asientos")
    cuenta = relationship("CatalogoCuentas")
    
    # TODO: Implementar validación de reglas de negocio:
    # Exactamente uno de 'debe' o 'haber' debe ser > 0
    # Esta validación se implementará en el servicio
    
    def __repr__(self):
        return f"<Asiento(id={self.id_asiento}, cuenta_id={self.id_cuenta}, debe={self.debe}, haber={self.haber})>"