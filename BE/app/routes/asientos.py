"""
Rutas de API para operaciones de Asientos Contables.
Proporciona endpoints CRUD para gestionar asientos contables.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from BE.app.db import get_db
from BE.app.schemas.asiento import AsientoCreate, AsientoRead, AsientoUpdate
from BE.app.services.asiento_service import (
    create_asiento, get_asiento, get_asientos, update_asiento, delete_asiento
)
from BE.app.services.transaccion_service import create_asiento_transaccion

from typing import List, Optional

router = APIRouter(prefix="/api/asientos", tags=["Asientos"])


# Crear asiento simple (facturas son independientes)
@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_asiento(asiento: AsientoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo asiento contable. Las facturas se manejan independientemente."""
    nuevo_asiento = create_asiento(db, asiento)
    return {"id_asiento": nuevo_asiento.id_asiento}


# Crear asiento asociado a una transacción específica
@router.post("/transaccion/{id_transaccion}", status_code=status.HTTP_201_CREATED, response_model=AsientoRead)
def crear_asiento_para_transaccion(
        id_transaccion: int,
        asiento: AsientoCreate,
        db: Session = Depends(get_db)
):
    """
    Crear un asiento contable asociado a una transacción específica.
    Las facturas se manejan de forma independiente en su propio módulo.

    Args:
        id_transaccion: ID de la transacción a la que pertenece el asiento
        asiento: Datos del asiento a crear
        db: Sesión de base de datos

    Returns:
        Asiento creado con su información completa
    """
    return create_asiento_transaccion(db, asiento, id_transaccion)


@router.get("/", response_model=List[AsientoRead])
def listar_asientos(
        skip: int = 0,
        limit: int = 100,
        id_transaccion: Optional[int] = Query(None, description="Filtrar por ID de transacción"),
        id_cuenta: Optional[int] = Query(None, description="Filtrar por ID de cuenta"),
        db: Session = Depends(get_db)
):
    """Obtener todos los asientos contables con filtros opcionales"""
    return get_asientos(
        db,
        skip=skip,
        limit=limit,
        id_transaccion=id_transaccion,
        id_cuenta=id_cuenta
    )


@router.get("/{asiento_id}", response_model=AsientoRead)
def obtener_asiento(asiento_id: int, db: Session = Depends(get_db)):
    """Obtener un asiento contable específico por ID"""
    return get_asiento(db, asiento_id)


@router.put("/{asiento_id}", response_model=AsientoRead)
def actualizar_asiento(
        asiento_id: int,
        asiento: AsientoUpdate,
        db: Session = Depends(get_db)
):
    """Actualizar un asiento contable existente"""
    return update_asiento(db, asiento_id, asiento)


@router.delete("/{asiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_asiento(asiento_id: int, db: Session = Depends(get_db)):
    """Eliminar un asiento contable"""
    delete_asiento(db, asiento_id)
    return None