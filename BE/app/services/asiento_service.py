"""
Capa de servicios para operaciones de Asientos Contables.
Maneja la lógica de negocio y operaciones de base de datos para asientos contables.
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.asiento import Asiento
from app.models.transaccion import Transaccion
from app.models.catalogo_cuentas import CatalogoCuentas
from app.schemas.asiento import AsientoCreate, AsientoUpdate
from typing import List, Optional
from decimal import Decimal

def validate_asiento_business_rules(debe: Decimal, haber: Decimal):
    """Validar que exactamente uno de debe o haber sea mayor que 0"""
    if (debe > 0 and haber > 0) or (debe == 0 and haber == 0):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exactamente uno de debe o haber debe ser mayor que 0"
        )

def create_asiento(db: Session, asiento_data: AsientoCreate) -> Asiento:
    """Crear un nuevo asiento contable"""
    # Validar que la transacción existe
    transaccion = db.query(Transaccion).filter(
        Transaccion.id_transaccion == asiento_data.id_transaccion
    ).first()
    if not transaccion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transacción no encontrada"
        )
    
    # Validar que la cuenta existe
    cuenta = db.query(CatalogoCuentas).filter(
        CatalogoCuentas.id_cuenta == asiento_data.id_cuenta
    ).first()
    if not cuenta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cuenta no encontrada"
        )
    
    # Validar reglas de negocio
    validate_asiento_business_rules(asiento_data.debe, asiento_data.haber)
    
    try:
        db_asiento = Asiento(**asiento_data.dict())
        db.add(db_asiento)
        db.commit()
        db.refresh(db_asiento)
        return db_asiento
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear asiento contable"
        )

def get_asiento(db: Session, asiento_id: int) -> Optional[Asiento]:
    """Obtener un asiento contable específico por ID"""
    asiento = db.query(Asiento).filter(Asiento.id_asiento == asiento_id).first()
    if not asiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asiento contable no encontrado"
        )
    return asiento

def get_asientos(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    id_transaccion: Optional[int] = None,
    id_cuenta: Optional[int] = None
) -> List[Asiento]:
    """Obtener asientos contables con filtros opcionales"""
    query = db.query(Asiento)
    
    if id_transaccion:
        query = query.filter(Asiento.id_transaccion == id_transaccion)
    if id_cuenta:
        query = query.filter(Asiento.id_cuenta == id_cuenta)
    
    return query.offset(skip).limit(limit).all()

def update_asiento(db: Session, asiento_id: int, asiento_data: AsientoUpdate) -> Asiento:
    """Actualizar un asiento contable existente"""
    asiento = get_asiento(db, asiento_id)
    update_data = asiento_data.dict(exclude_unset=True)
    
    # Validate transaction exists if being updated
    if 'id_transaccion' in update_data:
        transaccion = db.query(Transaccion).filter(
            Transaccion.id_transaccion == update_data['id_transaccion']
        ).first()
        if not transaccion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction not found"
            )
    
    # Validate account exists if being updated
    if 'id_cuenta' in update_data:
        cuenta = db.query(CatalogoCuentas).filter(
            CatalogoCuentas.id_cuenta == update_data['id_cuenta']
        ).first()
        if not cuenta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account not found"
            )
    
    # Apply updates and validate business rules
    for key, value in update_data.items():
        setattr(asiento, key, value)
    
    validate_asiento_business_rules(asiento.debe, asiento.haber)
    
    try:
        db.commit()
        db.refresh(asiento)
        return asiento
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating journal entry"
        )

def delete_asiento(db: Session, asiento_id: int) -> bool:
    """Eliminar un asiento contable"""
    asiento = get_asiento(db, asiento_id)
    db.delete(asiento)
    db.commit()
    return True