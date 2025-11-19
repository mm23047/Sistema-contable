"""
Servicio de gestión de productos y servicios.
Lógica de negocio para CRUD de productos/servicios.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fastapi import HTTPException, status
from typing import Optional, List
from decimal import Decimal

from BE.app.models.producto_servicio import ProductoServicio
from BE.app.schemas.producto_servicio_schemas import ProductoServicioCreate, ProductoServicioUpdate


# =========================================================
# 🟦 CREAR PRODUCTO/SERVICIO
# =========================================================
def crear_producto(db: Session, producto_data: ProductoServicioCreate) -> ProductoServicio:
    """
    Crea un nuevo producto o servicio.
    Valida que el código sea único si se proporciona.
    """
    # Validar código único si se proporciona
    if producto_data.codigo:
        producto_existente = db.query(ProductoServicio).filter(
            ProductoServicio.codigo == producto_data.codigo
        ).first()
        
        if producto_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un producto con código {producto_data.codigo}"
            )
    
    # Crear producto
    nuevo_producto = ProductoServicio(
        codigo=producto_data.codigo,
        nombre=producto_data.nombre,
        descripcion=producto_data.descripcion,
        tipo=producto_data.tipo,
        categoria=producto_data.categoria,
        precio_unitario=producto_data.precio_unitario,
        precio_costo=producto_data.precio_costo,
        unidad_medida=producto_data.unidad_medida,
        stock_actual=producto_data.stock_actual if producto_data.tipo == "PRODUCTO" else None,
        stock_minimo=producto_data.stock_minimo if producto_data.tipo == "PRODUCTO" else None,
        aplica_iva=producto_data.aplica_iva
    )
    
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    
    return nuevo_producto


# =========================================================
# 🟦 OBTENER PRODUCTO POR ID
# =========================================================
def obtener_producto_por_id(db: Session, producto_id: int) -> ProductoServicio:
    """Obtiene un producto por su ID"""
    producto = db.query(ProductoServicio).filter(
        ProductoServicio.id_producto == producto_id
    ).first()
    
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto {producto_id} no encontrado"
        )
    
    return producto


# =========================================================
# 🟦 LISTAR PRODUCTOS
# =========================================================
def listar_productos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busqueda: Optional[str] = None,
    tipo: Optional[str] = None,
    categoria: Optional[str] = None,
    activo: Optional[str] = None,
    bajo_stock: bool = False
) -> List[ProductoServicio]:
    """
    Lista productos/servicios con filtros opcionales.
    busqueda: busca en nombre, código, descripción
    tipo: PRODUCTO o SERVICIO
    categoria: categoría del producto
    activo: SI o NO
    bajo_stock: solo productos con stock < stock_minimo
    """
    query = db.query(ProductoServicio)
    
    # Filtro de búsqueda general
    if busqueda:
        busqueda_pattern = f"%{busqueda}%"
        query = query.filter(
            or_(
                ProductoServicio.nombre.ilike(busqueda_pattern),
                ProductoServicio.codigo.ilike(busqueda_pattern),
                ProductoServicio.descripcion.ilike(busqueda_pattern)
            )
        )
    
    # Filtro por tipo
    if tipo and tipo in ['PRODUCTO', 'SERVICIO']:
        query = query.filter(ProductoServicio.tipo == tipo)
    
    # Filtro por categoría
    if categoria:
        query = query.filter(ProductoServicio.categoria.ilike(f"%{categoria}%"))
    
    # Filtro por estado activo
    if activo and activo in ['SI', 'NO']:
        query = query.filter(ProductoServicio.activo == activo)
    
    # Filtro por bajo stock
    if bajo_stock:
        query = query.filter(
            ProductoServicio.tipo == "PRODUCTO",
            ProductoServicio.stock_actual < ProductoServicio.stock_minimo
        )
    
    return query.order_by(ProductoServicio.nombre).offset(skip).limit(limit).all()


# =========================================================
# 🟦 ACTUALIZAR PRODUCTO
# =========================================================
def actualizar_producto(
    db: Session,
    producto_id: int,
    producto_update: ProductoServicioUpdate
) -> ProductoServicio:
    """Actualiza un producto existente"""
    producto = obtener_producto_por_id(db, producto_id)
    
    # Validar código único si se está actualizando
    if producto_update.codigo and producto_update.codigo != producto.codigo:
        producto_existente = db.query(ProductoServicio).filter(
            ProductoServicio.codigo == producto_update.codigo,
            ProductoServicio.id_producto != producto_id
        ).first()
        
        if producto_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro producto con código {producto_update.codigo}"
            )
    
    # Actualizar campos proporcionados
    update_data = producto_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(producto, field, value)
    
    db.commit()
    db.refresh(producto)
    
    return producto


# =========================================================
# 🟦 ACTUALIZAR STOCK
# =========================================================
def actualizar_stock(
    db: Session,
    producto_id: int,
    cantidad: Decimal,
    operacion: str = "suma"  # "suma" o "resta"
) -> ProductoServicio:
    """
    Actualiza el stock de un producto.
    operacion: "suma" para ingresos, "resta" para ventas
    """
    producto = obtener_producto_por_id(db, producto_id)
    
    # Validar que sea un producto físico
    if producto.tipo != "PRODUCTO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede actualizar stock de un SERVICIO"
        )
    
    # Actualizar stock
    if operacion == "suma":
        producto.stock_actual = (producto.stock_actual or Decimal('0')) + cantidad
    elif operacion == "resta":
        nuevo_stock = (producto.stock_actual or Decimal('0')) - cantidad
        if nuevo_stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Disponible: {producto.stock_actual}, Solicitado: {cantidad}"
            )
        producto.stock_actual = nuevo_stock
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operación debe ser 'suma' o 'resta'"
        )
    
    db.commit()
    db.refresh(producto)
    
    return producto


# =========================================================
# 🟦 DESACTIVAR PRODUCTO
# =========================================================
def desactivar_producto(db: Session, producto_id: int) -> ProductoServicio:
    """Desactiva un producto (no lo elimina)"""
    producto = obtener_producto_por_id(db, producto_id)
    producto.activo = "NO"
    
    db.commit()
    db.refresh(producto)
    
    return producto


# =========================================================
# 🟦 BUSCAR PRODUCTO POR CÓDIGO
# =========================================================
def buscar_producto_por_codigo(db: Session, codigo: str) -> Optional[ProductoServicio]:
    """Busca un producto por su código SKU"""
    return db.query(ProductoServicio).filter(ProductoServicio.codigo == codigo).first()


# =========================================================
# 🟦 OBTENER PRODUCTOS CON BAJO STOCK
# =========================================================
def obtener_productos_bajo_stock(db: Session) -> List[ProductoServicio]:
    """Obtiene productos con stock actual menor al mínimo"""
    return db.query(ProductoServicio).filter(
        ProductoServicio.tipo == "PRODUCTO",
        ProductoServicio.activo == "SI",
        ProductoServicio.stock_actual < ProductoServicio.stock_minimo
    ).order_by(ProductoServicio.stock_actual).all()


# =========================================================
# 🟦 ESTADÍSTICAS DE PRODUCTOS
# =========================================================
def obtener_estadisticas_productos(db: Session):
    """Obtiene estadísticas generales de productos"""
    total = db.query(func.count(ProductoServicio.id_producto)).scalar()
    productos = db.query(func.count(ProductoServicio.id_producto)).filter(
        ProductoServicio.tipo == "PRODUCTO"
    ).scalar()
    servicios = db.query(func.count(ProductoServicio.id_producto)).filter(
        ProductoServicio.tipo == "SERVICIO"
    ).scalar()
    activos = db.query(func.count(ProductoServicio.id_producto)).filter(
        ProductoServicio.activo == "SI"
    ).scalar()
    bajo_stock = db.query(func.count(ProductoServicio.id_producto)).filter(
        ProductoServicio.tipo == "PRODUCTO",
        ProductoServicio.stock_actual < ProductoServicio.stock_minimo
    ).scalar()
    
    # Valor total del inventario
    valor_inventario = db.query(
        func.sum(ProductoServicio.stock_actual * ProductoServicio.precio_unitario)
    ).filter(
        ProductoServicio.tipo == "PRODUCTO"
    ).scalar() or Decimal('0')
    
    return {
        "total": total,
        "productos": productos,
        "servicios": servicios,
        "activos": activos,
        "inactivos": total - activos,
        "bajo_stock": bajo_stock,
        "valor_inventario": float(valor_inventario)
    }


# =========================================================
# 🟦 CALCULAR PRECIO CON IVA
# =========================================================
def calcular_precio_con_iva(
    precio_unitario: Decimal,
    aplica_iva: str,
    tasa_iva: Decimal = Decimal('0.13')
) -> Decimal:
    """Calcula el precio final incluyendo IVA si aplica"""
    if aplica_iva == "SI":
        return precio_unitario * (Decimal('1') + tasa_iva)
    return precio_unitario
