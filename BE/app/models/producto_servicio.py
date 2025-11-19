"""
Modelo de Producto/Servicio para el sistema de facturación.
Catálogo de productos y servicios vendibles.
"""
from sqlalchemy import Column, String, Integer, Numeric, TIMESTAMP, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from BE.app.db import Base


class ProductoServicio(Base):
    __tablename__ = "productos_servicios"
    __table_args__ = {'extend_existing': True}

    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    
    # Información básica
    codigo = Column(String(50), nullable=True, unique=True, index=True)  # SKU o código interno
    nombre = Column(String(150), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    
    # Tipo
    tipo = Column(String(20), nullable=False, default="PRODUCTO")  # PRODUCTO, SERVICIO
    categoria = Column(String(100), nullable=True)  # Electrónica, Alimentos, Consultoría, etc.
    
    # Precios
    precio_unitario = Column(Numeric(12, 2), nullable=False, default=0.00)
    precio_costo = Column(Numeric(12, 2), nullable=True, default=0.00)  # Para cálculo de utilidad
    
    # Inventario (solo para productos físicos)
    unidad_medida = Column(String(20), nullable=True, default="UNIDAD")  # UNIDAD, KG, M, L, etc.
    stock_actual = Column(Numeric(12, 2), nullable=True, default=0.00)
    stock_minimo = Column(Numeric(12, 2), nullable=True, default=0.00)
    
    # Impuestos
    aplica_iva = Column(String(10), nullable=False, default="SI")  # SI, NO
    
    # Estado
    activo = Column(String(10), nullable=False, default="SI")  # SI, NO
    
    # Auditoría
    fecha_registro = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relaciones
    detalles_factura = relationship("FacturaDetalle", back_populates="producto")
