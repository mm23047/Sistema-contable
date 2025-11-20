from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from BE.app.models.transaccion import Transaccion
from BE.app.models.periodo import PeriodoContable
from BE.app.models.asiento import Asiento
from BE.app.schemas.transaccion import TransaccionCreate, TransaccionUpdate
from typing import List, Optional
from datetime import datetime


# ---------------------------------------------------
# 🟦 CREAR TRANSACCIÓN
# ---------------------------------------------------
def create_transaccion(db: Session, transaccion_data: TransaccionCreate) -> Transaccion:

    # Validar período si aplica
    if transaccion_data.id_periodo:
        periodo = db.query(PeriodoContable).filter(
            PeriodoContable.id_periodo == transaccion_data.id_periodo
        ).first()
        if not periodo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de período inválido"
            )

    transaccion_dict = transaccion_data.dict()
    transaccion_dict["fecha_creacion"] = datetime.now()

    try:
        db_transaccion = Transaccion(**transaccion_dict)
        db.add(db_transaccion)
        db.commit()
        db.refresh(db_transaccion)
        return db_transaccion

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error creating transaction: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error creating transaction: {str(e)}"
        )


# ---------------------------------------------------
# 🟦 CREAR ASIENTO PARA UNA TRANSACCIÓN
# ---------------------------------------------------
def create_asiento_transaccion(db: Session, asiento_data: dict, id_transaccion: int) -> Asiento:
    """
    Crea un asiento contable asociado a una transacción.
    Las facturas se crean independientemente.
    """
    # Validar que la transacción existe
    get_transaccion(db, id_transaccion)

    try:
        # Crear asiento
        asiento_dict = asiento_data.copy() if isinstance(asiento_data, dict) else asiento_data.dict()
        asiento_dict["id_transaccion"] = id_transaccion

        db_asiento = Asiento(**asiento_dict)
        db.add(db_asiento)
        db.commit()
        db.refresh(db_asiento)

        return db_asiento

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error adding entry: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error adding entry: {str(e)}"
        )


# ---------------------------------------------------
# 🔍 Obtener transacción
# ---------------------------------------------------
def get_transaccion(db: Session, transaccion_id: int) -> Optional[Transaccion]:
    transaccion = db.query(Transaccion).filter(
        Transaccion.id_transaccion == transaccion_id
    ).first()
    if not transaccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return transaccion


# ---------------------------------------------------
# 🔍 Listar transacciones
# ---------------------------------------------------
def get_transacciones(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        fecha_from: Optional[datetime] = None,
        fecha_to: Optional[datetime] = None,
        id_periodo: Optional[int] = None,
        tipo: Optional[str] = None,
        categoria: Optional[str] = None
) -> List[Transaccion]:

    query = db.query(Transaccion)

    if fecha_from:
        query = query.filter(Transaccion.fecha_transaccion >= fecha_from)
    if fecha_to:
        query = query.filter(Transaccion.fecha_transaccion <= fecha_to)
    if id_periodo:
        query = query.filter(Transaccion.id_periodo == id_periodo)
    if tipo:
        query = query.filter(Transaccion.tipo == tipo)
    if categoria:
        query = query.filter(Transaccion.categoria == categoria)

    return query.offset(skip).limit(limit).all()


# ---------------------------------------------------
# 🟧 Actualizar transacción
# ---------------------------------------------------
def update_transaccion(db: Session, transaccion_id: int, transaccion_data: TransaccionUpdate) -> Transaccion:

    transaccion = get_transaccion(db, transaccion_id)
    update_data = transaccion_data.dict(exclude_unset=True)

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


# ---------------------------------------------------
# 🟥 Eliminar transacción
# ---------------------------------------------------
def delete_transaccion(db: Session, transaccion_id: int) -> bool:
    transaccion = get_transaccion(db, transaccion_id)
    db.delete(transaccion)
    db.commit()
    return True
