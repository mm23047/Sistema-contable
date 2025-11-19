from sqlalchemy import Column, String, Numeric, TIMESTAMP, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from BE.app.db import Base


class Factura(Base):
    __tablename__ = "facturas"
    __table_args__ = {'extend_existing': True}

    id_factura = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_factura = Column(String(50), nullable=False, unique=True)
    
    # Relación con cliente (NUEVO - normalizado)
    id_cliente = Column(
        Integer,
        ForeignKey("clientes.id_cliente", ondelete="RESTRICT"),
        nullable=True,  # Permitir null para facturas legacy
        index=True
    )
    
    # Campos legacy de cliente (mantener por compatibilidad, deprecar gradualmente)
    cliente = Column(String(150), nullable=True)  # Deprecar: usar cliente.nombre
    nit_cliente = Column(String(20), nullable=True)  # Deprecar: usar cliente.nit
    direccion_cliente = Column(String(255), nullable=True)  # Deprecar
    telefono_cliente = Column(String(20), nullable=True)  # Deprecar
    email_cliente = Column(String(100), nullable=True)  # Deprecar
    
    # Montos (calculados desde factura_detalle)
    subtotal = Column(Numeric(12, 2), nullable=False, default=0.00)
    descuento = Column(Numeric(12, 2), nullable=False, default=0.00)
    iva = Column(Numeric(12, 2), nullable=False, default=0.00)  # IVA 13%
    monto_total = Column(Numeric(12, 2), nullable=False)
    
    # Producto o Servicio (DEPRECAR - usar factura_detalle)
    producto_servicio = Column(Text, nullable=True)  # Mantener para facturas legacy
    
    # Información adicional
    notas = Column(Text, nullable=True)
    condiciones_pago = Column(String(100), nullable=True, default="Contado")
    vendedor = Column(String(100), nullable=True)
    
    # Fechas 
    fecha_emision = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    fecha_vencimiento = Column(TIMESTAMP, nullable=True)
    
    # Relaciones
    cliente_obj = relationship("Cliente", back_populates="facturas")
    detalles = relationship("FacturaDetalle", back_populates="factura", cascade="all, delete-orphan")

