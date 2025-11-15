"""
Rutas de API para operaciones de Períodos Contables.
Proporciona endpoints CRUD para gestionar períodos contables.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BE.app.db import get_db
from BE.app.schemas.periodo import PeriodoCreate, PeriodoRead, PeriodoUpdate
from BE.app.services.periodo_service import (
    create_periodo, get_periodo, get_periodos, get_periodos_activos, 
    update_periodo, delete_periodo
)
from typing import List

router = APIRouter(prefix="/api/periodos", tags=["Períodos Contables"])

@router.post("/", response_model=PeriodoRead, status_code=status.HTTP_201_CREATED)
def crear_periodo(periodo: PeriodoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo período contable"""
    return create_periodo(db, periodo)

@router.get("/", response_model=List[PeriodoRead])
def listar_periodos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener todos los períodos contables con paginación"""
    return get_periodos(db, skip=skip, limit=limit)

@router.get("/activos", response_model=List[PeriodoRead])
def listar_periodos_activos(db: Session = Depends(get_db)):
    """Obtener solo períodos con estado ABIERTO para transacciones"""
    return get_periodos_activos(db)

@router.get("/{periodo_id}", response_model=PeriodoRead)
def obtener_periodo(periodo_id: int, db: Session = Depends(get_db)):
    """Obtener un período específico por ID"""
    return get_periodo(db, periodo_id)

@router.put("/{periodo_id}", response_model=PeriodoRead)
def actualizar_periodo(periodo_id: int, periodo: PeriodoUpdate, db: Session = Depends(get_db)):
    """Actualizar un período contable existente"""
    return update_periodo(db, periodo_id, periodo)

@router.delete("/{periodo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_periodo(periodo_id: int, db: Session = Depends(get_db)):
    """Eliminar un período contable"""
    delete_periodo(db, periodo_id)
    return None