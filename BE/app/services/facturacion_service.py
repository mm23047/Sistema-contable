"""
Servicio de facturación con lógica de negocio completa.
Maneja la creación, actualización y cálculos de facturas con arquitectura normalizada.
Soporta multi-línea de productos/servicios y gestión de inventario.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional, List
import uuid

from BE.app.models.factura_models import Factura
from BE.app.models.factura_detalle import FacturaDetalle
from BE.app.models.cliente import Cliente
from BE.app.models.producto_servicio import ProductoServicio
from BE.app.schemas.factura_schemas import FacturaCreate, FacturaUpdate


# =========================================================
# 🟦 GENERACIÓN DE NÚMERO DE FACTURA
# =========================================================
def generar_numero_factura(db: Session) -> str:
    """
    Genera un número de factura único en formato: FACT-YYYY-NNNN
    Ejemplo: FACT-2025-0001
    """
    año_actual = datetime.now().year
    
    # Buscar el último número del año actual
    ultima_factura = db.query(Factura).filter(
        Factura.numero_factura.like(f"FACT-{año_actual}-%")
    ).order_by(Factura.numero_factura.desc()).first()
    
    if ultima_factura:
        # Extraer el número secuencial
        partes = ultima_factura.numero_factura.split('-')
        if len(partes) == 3:
            try:
                ultimo_num = int(partes[2])
                nuevo_num = ultimo_num + 1
            except ValueError:
                nuevo_num = 1
        else:
            nuevo_num = 1
    else:
        nuevo_num = 1
    
    # Formatear con 4 dígitos: FACT-2025-0001
    return f"FACT-{año_actual}-{nuevo_num:04d}"


# =========================================================
# 🟦 CALCULAR IVA AUTOMÁTICAMENTE
# =========================================================
def calcular_iva(subtotal: Decimal, tasa_iva: Decimal = Decimal('0.13')) -> Decimal:
    """
    Calcula el IVA basado en el subtotal.
    Por defecto usa 13% (El Salvador, Guatemala, etc.)
    """
    return round(subtotal * tasa_iva, 2)


# =========================================================
# 🟦 CALCULAR MONTO TOTAL
# =========================================================
def calcular_monto_total(
    subtotal: Decimal,
    descuento: Decimal = Decimal('0.00'),
    iva: Decimal = Decimal('0.00')
) -> Decimal:
    """Calcula el monto total: Subtotal - Descuento + IVA"""
    return round(subtotal - descuento + iva, 2)


# =========================================================
# 🟦 CREAR FACTURA CON DETALLES (NORMALIZADA)
# =========================================================
def crear_factura(
    db: Session,
    factura_data: FacturaCreate,
    detalles: Optional[List[dict]] = None
) -> Factura:
    """
    Crea una nueva factura normalizada con cliente y detalles de productos.
    
    Args:
        factura_data: Datos de la factura (ahora debe incluir id_cliente)
        detalles: Lista de líneas con {id_producto, cantidad, precio_unitario, descuento_%}
    
    Proceso:
    1. Valida que el cliente existe
    2. Genera número de factura único
    3. Calcula totales basados en detalles de productos
    4. Crea factura principal
    5. Crea líneas de detalle
    6. Actualiza stock de productos (si aplica)
    """
    # 1. Validar cliente
    if factura_data.id_cliente:
        cliente = db.query(Cliente).filter(Cliente.id_cliente == factura_data.id_cliente).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cliente ID {factura_data.id_cliente} no encontrado"
            )
        if cliente.activo != 'SI':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cliente {cliente.nombre} está inactivo"
            )
    
    # 2. Generar número de factura
    numero_factura = generar_numero_factura(db)
    
    # 3. Calcular fecha de vencimiento (30 días por defecto para crédito)
    fecha_vencimiento = factura_data.fecha_vencimiento
    if not fecha_vencimiento and factura_data.condiciones_pago != "Contado":
        fecha_vencimiento = datetime.now() + timedelta(days=30)
    
    # 4. Si hay detalles de productos, calcular totales automáticamente
    subtotal_calculado = Decimal('0.00')
    iva_calculado = Decimal('0.00')
    
    if detalles:
        for detalle in detalles:
            producto = db.query(ProductoServicio).filter(
                ProductoServicio.id_producto == detalle['id_producto']
            ).first()
            
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto ID {detalle['id_producto']} no encontrado"
                )
            
            if producto.activo != 'SI':
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Producto {producto.nombre} está inactivo"
                )
            
            # Validar stock para productos físicos
            if producto.tipo == 'PRODUCTO':
                stock_actual = producto.stock_actual or 0
                if stock_actual < detalle['cantidad']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Stock insuficiente para {producto.nombre}. Disponible: {stock_actual}, Solicitado: {detalle['cantidad']}"
                    )
            
            # Calcular línea
            precio = detalle.get('precio_unitario', producto.precio_unitario)
            cantidad = Decimal(str(detalle['cantidad']))
            desc_porcentaje = Decimal(str(detalle.get('descuento_porcentaje', 0)))
            
            subtotal_linea = precio * cantidad
            desc_monto = round(subtotal_linea * (desc_porcentaje / Decimal('100')), 2)
            subtotal_linea = subtotal_linea - desc_monto
            
            if producto.aplica_iva == 'SI':
                iva_linea = round(subtotal_linea * Decimal('0.13'), 2)
            else:
                iva_linea = Decimal('0.00')
            
            subtotal_calculado += subtotal_linea
            iva_calculado += iva_linea
    
    # Usar valores calculados o los proporcionados
    subtotal_final = subtotal_calculado if detalles else factura_data.subtotal
    iva_final = iva_calculado if detalles else factura_data.iva
    descuento_final = factura_data.descuento or Decimal('0.00')
    monto_total_final = subtotal_final + iva_final - descuento_final
    
    # 5. Crear factura principal
    nueva_factura = Factura(
        numero_factura=numero_factura,
        id_cliente=factura_data.id_cliente,
        # Campos legacy (compatibilidad)
        cliente=factura_data.cliente,
        nit_cliente=factura_data.nit_cliente,
        direccion_cliente=factura_data.direccion_cliente,
        telefono_cliente=factura_data.telefono_cliente,
        email_cliente=factura_data.email_cliente,
        producto_servicio=factura_data.producto_servicio,
        subtotal=subtotal_final,
        descuento=descuento_final,
        iva=iva_final,
        monto_total=monto_total_final,
        notas=factura_data.notas,
        condiciones_pago=factura_data.condiciones_pago,
        vendedor=factura_data.vendedor,
        fecha_vencimiento=fecha_vencimiento
    )
    
    db.add(nueva_factura)
    db.flush()  # Para obtener id_factura antes de commit
    
    # 6. Crear líneas de detalle y actualizar stock
    if detalles:
        for detalle in detalles:
            producto = db.query(ProductoServicio).filter(
                ProductoServicio.id_producto == detalle['id_producto']
            ).first()
            
            precio = detalle.get('precio_unitario', producto.precio_unitario)
            cantidad = Decimal(str(detalle['cantidad']))
            desc_porcentaje = Decimal(str(detalle.get('descuento_porcentaje', 0)))
            desc_monto = detalle.get('descuento_monto', Decimal('0.00'))
            
            subtotal_linea = precio * cantidad
            desc_total = desc_monto + round(subtotal_linea * (desc_porcentaje / Decimal('100')), 2)
            subtotal_linea = subtotal_linea - desc_total
            
            if producto.aplica_iva == 'SI':
                iva_linea = round(subtotal_linea * Decimal('0.13'), 2)
            else:
                iva_linea = Decimal('0.00')
            
            total_linea = subtotal_linea + iva_linea
            
            # Crear detalle
            nuevo_detalle = FacturaDetalle(
                id_factura=nueva_factura.id_factura,
                id_producto=detalle['id_producto'],
                cantidad=cantidad,
                precio_unitario=precio,
                descuento_porcentaje=desc_porcentaje,
                descuento_monto=desc_monto,
                subtotal=subtotal_linea,
                iva=iva_linea,
                total=total_linea
            )
            db.add(nuevo_detalle)
            
            # Actualizar stock si es producto físico
            if producto.tipo == 'PRODUCTO':
                producto.stock_actual = (producto.stock_actual or 0) - cantidad
    
    db.commit()
    db.refresh(nueva_factura)
    
    return nueva_factura


# =========================================================
# 🟦 OBTENER FACTURA POR ID
# =========================================================
def obtener_factura_por_id(db: Session, factura_id: uuid.UUID) -> Optional[Factura]:
    """Obtiene una factura por su ID"""
    return db.query(Factura).filter(Factura.id_factura == factura_id).first()


# =========================================================
# 🟦 OBTENER FACTURA POR NÚMERO
# =========================================================
def obtener_factura_por_numero(db: Session, numero_factura: str) -> Optional[Factura]:
    """Obtiene una factura por su número"""
    return db.query(Factura).filter(Factura.numero_factura == numero_factura).first()


# =========================================================
# 🟦 LISTAR FACTURAS CON FILTROS
# =========================================================
def listar_facturas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    cliente: Optional[str] = None,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None
) -> List[Factura]:
    """Lista facturas con filtros opcionales"""
    query = db.query(Factura)
    
    if cliente:
        query = query.filter(Factura.cliente.ilike(f"%{cliente}%"))
    
    if fecha_desde:
        query = query.filter(Factura.fecha_emision >= fecha_desde)
    
    if fecha_hasta:
        query = query.filter(Factura.fecha_emision <= fecha_hasta)
    
    return query.order_by(Factura.fecha_emision.desc()).offset(skip).limit(limit).all()


# =========================================================
# 🟦 ACTUALIZAR FACTURA
# =========================================================
def actualizar_factura(
    db: Session,
    factura_id: uuid.UUID,
    factura_update: FacturaUpdate
) -> Factura:
    """Actualiza una factura existente (solo campos permitidos)"""
    factura = obtener_factura_por_id(db, factura_id)
    
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factura {factura_id} no encontrada"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = factura_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(factura, field, value)
    
    db.commit()
    db.refresh(factura)
    
    return factura


# =========================================================
# 🟦 ELIMINAR FACTURA
# =========================================================
def eliminar_factura(db: Session, factura_id: uuid.UUID) -> bool:
    """Elimina una factura"""
    factura = obtener_factura_por_id(db, factura_id)
    
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factura {factura_id} no encontrada"
        )
    
    db.delete(factura)
    db.commit()
    
    return True


# =========================================================
# 🟦 ESTADÍSTICAS DE FACTURACIÓN
# =========================================================
def obtener_estadisticas_facturacion(
    db: Session,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None
) -> dict:
    """Obtiene estadísticas de facturación en un rango de fechas"""
    query = db.query(
        func.count(Factura.id_factura).label('total_facturas'),
        func.sum(Factura.monto_total).label('total_ventas'),
        func.sum(Factura.subtotal).label('total_subtotal'),
        func.sum(Factura.iva).label('total_iva'),
        func.sum(Factura.descuento).label('total_descuentos'),
        func.avg(Factura.monto_total).label('promedio_venta')
    )
    
    if fecha_desde:
        query = query.filter(Factura.fecha_emision >= fecha_desde)
    
    if fecha_hasta:
        query = query.filter(Factura.fecha_emision <= fecha_hasta)
    
    resultado = query.first()
    
    return {
        "total_facturas": resultado.total_facturas or 0,
        "total_ventas": float(resultado.total_ventas or 0),
        "total_subtotal": float(resultado.total_subtotal or 0),
        "total_iva": float(resultado.total_iva or 0),
        "total_descuentos": float(resultado.total_descuentos or 0),
        "promedio_venta": float(resultado.promedio_venta or 0)
    }


# =========================================================
# 🟦 TOP CLIENTES (ACTUALIZADO PARA TABLA NORMALIZADA)
# =========================================================
def obtener_top_clientes(
    db: Session,
    limite: int = 10,
    fecha_desde: Optional[datetime] = None,
    fecha_hasta: Optional[datetime] = None
) -> List[dict]:
    """Obtiene los clientes con más compras (usa tabla normalizada)"""
    query = db.query(
        Cliente.id_cliente,
        Cliente.nombre,
        Cliente.nit,
        func.count(Factura.id_factura).label('total_compras'),
        func.sum(Factura.monto_total).label('monto_total_compras')
    ).join(Factura, Cliente.id_cliente == Factura.id_cliente)\
     .group_by(Cliente.id_cliente, Cliente.nombre, Cliente.nit)
    
    if fecha_desde:
        query = query.filter(Factura.fecha_emision >= fecha_desde)
    
    if fecha_hasta:
        query = query.filter(Factura.fecha_emision <= fecha_hasta)
    
    resultados = query.order_by(
        func.sum(Factura.monto_total).desc()
    ).limit(limite).all()
    
    return [
        {
            "id_cliente": r.id_cliente,
            "cliente": r.nombre,
            "nit_cliente": r.nit,
            "total_compras": r.total_compras,
            "monto_total_compras": float(r.monto_total_compras)
        }
        for r in resultados
    ]
