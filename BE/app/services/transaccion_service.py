"""
Capa de servicios para operaciones de Transacciones.
Maneja la lógica de negocio y operaciones de base de datos para transacciones.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from BE.app.models.transaccion import Transaccion
from BE.app.models.periodo import PeriodoContable
from BE.app.schemas.transaccion import TransaccionCreate, TransaccionUpdate
from typing import List, Optional
from datetime import datetime

def create_transaccion(db: Session, transaccion_data: TransaccionCreate) -> Transaccion:
    """Crear una nueva transacción"""
    # Validar que el período existe si se proporciona
    if transaccion_data.id_periodo:
        periodo = db.query(PeriodoContable).filter(
            PeriodoContable.id_periodo == transaccion_data.id_periodo
        ).first()
        if not periodo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de período inválido"
            )
    
    # Crear transacción con timestamp actual
    transaccion_dict = transaccion_data.dict()
    transaccion_dict['fecha_creacion'] = datetime.now()
    
    try:
        db_transaccion = Transaccion(**transaccion_dict)
        db.add(db_transaccion)
        db.commit()
        db.refresh(db_transaccion)
        return db_transaccion
    except IntegrityError as e:
        db.rollback()
        print(f"IntegrityError: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating transaction: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        print(f"General error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating transaction: {str(e)}"
        )

def get_transaccion(db: Session, transaccion_id: int) -> Optional[Transaccion]:
    """Obtener una transacción específica por ID"""
    transaccion = db.query(Transaccion).filter(
        Transaccion.id_transaccion == transaccion_id
    ).first()
    if not transaccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return transaccion

def get_transacciones(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    fecha_from: Optional[datetime] = None,
    fecha_to: Optional[datetime] = None,
    id_periodo: Optional[int] = None,
    tipo: Optional[str] = None
) -> List[Transaccion]:
    """Obtener transacciones con filtros opcionales"""
    query = db.query(Transaccion)
    
    if fecha_from:
        query = query.filter(Transaccion.fecha_transaccion >= fecha_from)
    if fecha_to:
        query = query.filter(Transaccion.fecha_transaccion <= fecha_to)
    if id_periodo:
        query = query.filter(Transaccion.id_periodo == id_periodo)
    if tipo:
        query = query.filter(Transaccion.tipo == tipo)
    
    return query.offset(skip).limit(limit).all()

def update_transaccion(db: Session, transaccion_id: int, transaccion_data: TransaccionUpdate) -> Transaccion:
    """Actualizar una transacción existente"""
    transaccion = get_transaccion(db, transaccion_id)
    update_data = transaccion_data.dict(exclude_unset=True)
    
    # Validar período si se está actualizando
    if 'id_periodo' in update_data and update_data['id_periodo']:
        periodo = db.query(PeriodoContable).filter(
            PeriodoContable.id_periodo == update_data['id_periodo']
        ).first()
        if not periodo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid period ID"
            )
    
    try:
        for key, value in update_data.items():
            setattr(transaccion, key, value)
        db.commit()
        db.refresh(transaccion)
        return transaccion
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating transaction"
        )

def delete_transaccion(db: Session, transaccion_id: int) -> bool:
    """Eliminar una transacción"""
    transaccion = get_transaccion(db, transaccion_id)
    
    # TODO: Definir política de cascada - actualmente implementa eliminación en cascada
    # Alternativa: marcar como inactivo en lugar de eliminar
    
    db.delete(transaccion)
    db.commit()
    return True