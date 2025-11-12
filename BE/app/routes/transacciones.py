"""
Rutas de API para operaciones de Transacciones.
Proporciona endpoints CRUD para gestionar transacciones contables.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from BE.app.db import get_db
from BE.app.schemas.transaccion import TransaccionCreate, TransaccionRead, TransaccionUpdate
from BE.app.services.transaccion_service import (
    create_transaccion, get_transaccion, get_transacciones, update_transaccion, delete_transaccion
)
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/transacciones", tags=["Transacciones"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_transaccion(transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    """Crear una nueva transacción"""
    nueva_transaccion = create_transaccion(db, transaccion)
    return {"id_transaccion": nueva_transaccion.id_transaccion}

@router.get("/", response_model=List[TransaccionRead])
def listar_transacciones(
    skip: int = 0,
    limit: int = 100,
    fecha_from: Optional[datetime] = Query(None, description="Filter from date"),
    fecha_to: Optional[datetime] = Query(None, description="Filter to date"),
    id_periodo: Optional[int] = Query(None, description="Filter by period ID"),
    tipo: Optional[str] = Query(None, description="Filter by type (INGRESO/EGRESO)"),
    db: Session = Depends(get_db)
):
    """Obtener todas las transacciones con filtros opcionales"""
    return get_transacciones(
        db, 
        skip=skip, 
        limit=limit,
        fecha_from=fecha_from,
        fecha_to=fecha_to,
        id_periodo=id_periodo,
        tipo=tipo
    )

@router.get("/{transaccion_id}", response_model=TransaccionRead)
def obtener_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    """Obtener una transacción específica por ID"""
    return get_transaccion(db, transaccion_id)

@router.put("/{transaccion_id}", response_model=TransaccionRead)
def actualizar_transaccion(
    transaccion_id: int, 
    transaccion: TransaccionUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar una transacción existente"""
    return update_transaccion(db, transaccion_id, transaccion)

@router.delete("/{transaccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    """Eliminar una transacción"""
    # TODO: Definir política de cascada para asientos relacionados
    delete_transaccion(db, transaccion_id)
    return None