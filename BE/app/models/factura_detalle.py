"""
Modelo de Detalle de Factura (líneas de factura).
Tabla que relaciona facturas con productos/servicios incluyendo cantidad y precios.
"""
from sqlalchemy import Column, Integer, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from BE.app.db import Base


class FacturaDetalle(Base):
    __tablename__ = "factura_detalle"
    __table_args__ = {'extend_existing': True}

    id_detalle = Column(Integer, primary_key=True, autoincrement=True)
    
    # Relaciones
    id_factura = Column(
        UUID(as_uuid=True),
        ForeignKey("facturas.id_factura", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    id_producto = Column(
        Integer,
        ForeignKey("productos_servicios.id_producto", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    
    # Detalles del ítem
    descripcion = Column(Text, nullable=True)  # Descripción adicional o personalizada
    cantidad = Column(Numeric(12, 2), nullable=False, default=1.00)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    
    # Descuentos a nivel de línea
    descuento_porcentaje = Column(Numeric(5, 2), nullable=True, default=0.00)  # Ej: 10.00 = 10%
    descuento_monto = Column(Numeric(12, 2), nullable=True, default=0.00)
    
    # Subtotal e IVA por línea
    subtotal = Column(Numeric(12, 2), nullable=False)  # cantidad * precio_unitario - descuento
    iva = Column(Numeric(12, 2), nullable=False, default=0.00)
    total = Column(Numeric(12, 2), nullable=False)  # subtotal + iva
    
    # Relaciones
    factura = relationship("Factura", back_populates="detalles")
    producto = relationship("ProductoServicio", back_populates="detalles_factura")
