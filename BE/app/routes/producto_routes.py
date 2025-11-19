"""
Rutas de API para operaciones de Productos y Servicios.
Proporciona endpoints CRUD para gestión del catálogo.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from BE.app.db import get_db
from BE.app.schemas.producto_servicio_schemas import (
    ProductoServicioCreate, 
    ProductoServicioUpdate, 
    ProductoServicioOut, 
    ProductoServicioResumen
)
from BE.app.services.producto_servicio_service import (
    crear_producto,
    obtener_producto_por_id,
    listar_productos,
    actualizar_producto,
    actualizar_stock,
    desactivar_producto,
    buscar_producto_por_codigo,
    obtener_productos_bajo_stock,
    obtener_estadisticas_productos,
    calcular_precio_con_iva
)

router = APIRouter(prefix="/api/productos", tags=["Productos y Servicios"])


# =========================================================
# 🟩 CREAR PRODUCTO/SERVICIO
# =========================================================
@router.post("/", response_model=ProductoServicioOut, status_code=status.HTTP_201_CREATED)
def crear_nuevo_producto(
    producto: ProductoServicioCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo producto o servicio.
    - Valida código SKU único
    - Tipo: PRODUCTO o SERVICIO
    """
    return crear_producto(db, producto)


# =========================================================
# 🟩 LISTAR PRODUCTOS/SERVICIOS
# =========================================================
@router.get("/", response_model=List[ProductoServicioOut])
def listar_todos_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busqueda: Optional[str] = Query(None, description="Buscar en nombre, código o descripción"),
    tipo: Optional[str] = Query(None, description="PRODUCTO o SERVICIO"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    activo: Optional[str] = Query(None, description="SI o NO"),
    bajo_stock: bool = Query(False, description="Solo productos con bajo stock"),
    db: Session = Depends(get_db)
):
    """
    Lista productos y servicios con filtros.
    - busqueda: busca en nombre, código y descripción
    - tipo: PRODUCTO o SERVICIO
    - categoria: categoría específica
    - activo: SI o NO
    - bajo_stock: true para alertas de inventario
    """
    return listar_productos(db, skip, limit, busqueda, tipo, categoria, activo, bajo_stock)


# =========================================================
# 🟩 OBTENER PRODUCTO POR ID
# =========================================================
@router.get("/{producto_id}", response_model=ProductoServicioOut)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene un producto/servicio específico por ID"""
    return obtener_producto_por_id(db, producto_id)


# =========================================================
# 🟩 BUSCAR PRODUCTO POR CÓDIGO
# =========================================================
@router.get("/buscar/codigo/{codigo}", response_model=ProductoServicioOut)
def buscar_por_codigo(
    codigo: str,
    db: Session = Depends(get_db)
):
    """Busca un producto/servicio por su código SKU"""
    producto = buscar_producto_por_codigo(db, codigo)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró producto con código {codigo}"
        )
    return producto


# =========================================================
# 🟩 ACTUALIZAR PRODUCTO/SERVICIO
# =========================================================
@router.put("/{producto_id}", response_model=ProductoServicioOut)
def actualizar_producto_existente(
    producto_id: int,
    producto: ProductoServicioUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza los datos de un producto/servicio"""
    return actualizar_producto(db, producto_id, producto)


# =========================================================
# 🟩 ACTUALIZAR STOCK
# =========================================================
@router.patch("/{producto_id}/stock", response_model=ProductoServicioOut)
def modificar_stock(
    producto_id: int,
    cantidad: Decimal = Query(..., description="Cantidad a sumar (positiva) o restar (negativa)"),
    db: Session = Depends(get_db)
):
    """
    Actualiza el stock de un producto.
    - cantidad positiva: suma al stock (compra)
    - cantidad negativa: resta del stock (venta)
    Valida stock insuficiente.
    """
    return actualizar_stock(db, producto_id, cantidad)


# =========================================================
# 🟩 DESACTIVAR PRODUCTO
# =========================================================
@router.patch("/{producto_id}/desactivar", response_model=ProductoServicioOut)
def desactivar_producto_existente(
    producto_id: int,
    db: Session = Depends(get_db)
):
    """
    Desactiva un producto/servicio (marca como inactivo).
    Mejor práctica que eliminarlo.
    """
    return desactivar_producto(db, producto_id)


# =========================================================
# 🟩 OBTENER PRODUCTOS BAJO STOCK
# =========================================================
@router.get("/alertas/bajo-stock", response_model=List[ProductoServicioResumen])
def productos_bajo_stock(db: Session = Depends(get_db)):
    """
    Lista productos con stock actual menor al mínimo.
    Útil para alertas de reabastecimiento.
    """
    return obtener_productos_bajo_stock(db)


# =========================================================
# 🟩 ESTADÍSTICAS DE PRODUCTOS
# =========================================================
@router.get("/estadisticas/resumen")
def obtener_estadisticas(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas del catálogo.
    - Total productos/servicios
    - Activos vs inactivos
    - Valor total del inventario
    - Productos bajo stock
    """
    return obtener_estadisticas_productos(db)


# =========================================================
# 🟩 CALCULAR PRECIO CON IVA
# =========================================================
@router.get("/{producto_id}/precio-iva")
def obtener_precio_con_iva(
    producto_id: int,
    db: Session = Depends(get_db)
):
    """
    Calcula el precio final con IVA.
    Solo si aplica_iva es True.
    """
    precio = calcular_precio_con_iva(db, producto_id)
    return {
        "id_producto": producto_id,
        "precio_con_iva": precio
    }
