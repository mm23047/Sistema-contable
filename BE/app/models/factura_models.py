from sqlalchemy import Column, String, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from BE.app.db import Base


class Factura(Base):
    __tablename__ = "facturas"

    id_factura = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    numero_factura = Column(String, nullable=False)
    cliente = Column(String, nullable=False)
    monto_total = Column(Numeric(12, 2), nullable=False)
    fecha_emision = Column(TIMESTAMP, server_default=func.now())
    id_transaccion = Column(
        ForeignKey("transacciones.id_transaccion", ondelete="CASCADE"),
        nullable=False
    )
