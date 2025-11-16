"""
Rutas de API para operaciones de Transacciones.
Proporciona endpoints CRUD para gestionar transacciones contables.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from BE.app.db import get_db
from BE.app.schemas.transaccion import (
    TransaccionCreate,
    TransaccionRead,
    TransaccionUpdate
)
from BE.app.services.transaccion_service import (
    create_transaccion,
    get_transaccion,
    get_transacciones,
    update_transaccion,
    delete_transaccion
)
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/transacciones", tags=["Transacciones"])


# ============================================================
# 🟢 POST — CREAR TRANSACCIÓN (Si es VENTA → factura automática)
# ============================================================
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_transaccion_route(
    transaccion: TransaccionCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva transacción.
    Si la categoría es 'VENTA', se genera automáticamente una factura ligada.
    """
    nueva_transaccion = create_transaccion(db, transaccion)

    return {
        "id_transaccion": nueva_transaccion.id_transaccion,
        "categoria": nueva_transaccion.categoria,
        "factura_creada": getattr(nueva_transaccion, "factura_creada", False)
    }


# ============================================================
# 🟡 GET — LISTAR TRANSACCIONES
# ============================================================
@router.get("/", response_model=List[TransaccionRead])
def listar_transacciones_route(
    skip: int = 0,
    limit: int = 100,
    fecha_from: Optional[datetime] = Query(None, description="Filter from date"),
    fecha_to: Optional[datetime] = Query(None, description="Filter to date"),
    id_periodo: Optional[int] = Query(None, description="Filter by period ID"),
    tipo: Optional[str] = Query(None, description="Filter by type (INGRESO/EGRESO)"),
    categoria: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Lista transacciones con múltiples filtros opcionales.
    """
    return get_transacciones(
        db,
        skip=skip,
        limit=limit,
        fecha_from=fecha_from,
        fecha_to=fecha_to,
        id_periodo=id_periodo,
        tipo=tipo,
        categoria=categoria
    )


# ============================================================
# 🟡 GET — OBTENER UNA TRANSACCIÓN POR ID
# ============================================================
@router.get("/{transaccion_id}", response_model=TransaccionRead)
def obtener_transaccion_route(
    transaccion_id: int,
    db: Session = Depends(get_db)
):
    """
    Retorna una única transacción por ID.
    """
    return get_transaccion(db, transaccion_id)


# ============================================================
# 🟠 PUT — ACTUALIZAR TRANSACCIÓN
# ============================================================
@router.put("/{transaccion_id}", response_model=TransaccionRead)
def actualizar_transaccion_route(
    transaccion_id: int,
    transaccion: TransaccionUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una transacción existente.
    """
    return update_transaccion(db, transaccion_id, transaccion)


# ============================================================
# 🔴 DELETE — ELIMINAR TRANSACCIÓN
# ============================================================
@router.delete("/{transaccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transaccion_route(
    transaccion_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina una transacción y sus datos asociados según la política definida.
    """
    delete_transaccion(db, transaccion_id)
    return None
