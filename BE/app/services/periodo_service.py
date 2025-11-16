"""
Capa de servicios para operaciones de Períodos Contables.
Maneja la lógica de negocio y operaciones de base de datos para períodos.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from BE.app.models.periodo import PeriodoContable
from BE.app.schemas.periodo import PeriodoCreate, PeriodoUpdate
from typing import List, Optional

def create_periodo(db: Session, periodo_data: PeriodoCreate) -> PeriodoContable:
    """Crear un nuevo período contable"""
    try:
        db_periodo = PeriodoContable(**periodo_data.dict())
        db.add(db_periodo)
        db.commit()
        db.refresh(db_periodo)
        return db_periodo
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear período contable"
        )

def get_periodo(db: Session, periodo_id: int) -> Optional[PeriodoContable]:
    """Obtener un período específico por ID"""
    periodo = db.query(PeriodoContable).filter(PeriodoContable.id_periodo == periodo_id).first()
    if not periodo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Período contable no encontrado"
        )
    return periodo

def get_periodos(db: Session, skip: int = 0, limit: int = 100) -> List[PeriodoContable]:
    """Obtener todos los períodos con paginación"""
    return db.query(PeriodoContable).offset(skip).limit(limit).all()

def get_periodos_activos(db: Session) -> List[PeriodoContable]:
    """Obtener solo períodos con estado ABIERTO"""
    return db.query(PeriodoContable).filter(PeriodoContable.estado == 'ABIERTO').all()

def update_periodo(db: Session, periodo_id: int, periodo_data: PeriodoUpdate) -> PeriodoContable:
    """Actualizar un período existente"""
    periodo = get_periodo(db, periodo_id)
    update_data = periodo_data.dict(exclude_unset=True)
    
    try:
        for key, value in update_data.items():
            setattr(periodo, key, value)
        db.commit()
        db.refresh(periodo)
        return periodo
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar período contable"
        )

def delete_periodo(db: Session, periodo_id: int) -> bool:
    """Eliminar un período contable"""
    periodo = get_periodo(db, periodo_id)
    
    # TODO: Verificar si el período tiene transacciones asociadas antes de eliminar
    # Por ahora, permitimos la eliminación
    
    db.delete(periodo)
    db.commit()
    return True