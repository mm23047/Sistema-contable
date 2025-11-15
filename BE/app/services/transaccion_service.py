from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from BE.app.models.factura_models import Factura
from BE.app.models.transaccion import Transaccion
from BE.app.models.periodo import PeriodoContable
from BE.app.models.asiento import Asiento
from BE.app.schemas.transaccion import TransaccionCreate, TransaccionUpdate
from typing import List, Optional
from datetime import datetime


# ---------------------------------------------------
# 🟦 FUNCIÓN: crear factura automática para VENTAS
# ---------------------------------------------------
def crear_factura_automatica(db: Session, transaccion: Transaccion):
    # 1. Obtener número correlativo
    ultimo_numero = (
        db.query(Factura)
        .order_by(Factura.numero_factura.desc())
        .first()
    )
    nuevo_numero = 1 if ultimo_numero is None else ultimo_numero.numero_factura + 1

    # 2. Cargar los asientos de la transacción
    asientos = db.query(Asiento).filter(
        Asiento.id_transaccion == transaccion.id_transaccion
    ).all()

    if not asientos:
        raise HTTPException(
            status_code=400,
            detail="No se pueden generar facturas: la transacción no tiene asientos."
        )

    # 3. Calcular monto_total = SUMA(debe + haber)
    monto_total = sum(
        float(a.debe or 0) + float(a.haber or 0)
        for a in asientos
    )

    # 4. Crear factura
    factura = Factura(
        id_transaccion=transaccion.id_transaccion,
        numero_factura=nuevo_numero,
        cliente=transaccion.usuario_creacion,  # <-- nombre del cliente/usuario
        monto_total=monto_total,
        fecha_emision=datetime.now()
    )

    db.add(factura)
    db.commit()
    db.refresh(factura)
    return factura


# ---------------------------------------------------
# 🟦 CREAR TRANSACCIÓN (SIN validar asientos)
# ---------------------------------------------------
def create_transaccion(db: Session, transaccion_data: TransaccionCreate) -> Transaccion:
    # Validar período si se envía
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
    # ❌ REMOVIDO: No agregar factura_creada aquí

    try:
        # Crear transacción sin validar asientos
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
# 🟦 AGREGAR ASIENTO Y GENERAR FACTURA SI APLICA
# ---------------------------------------------------
def agregar_asiento_y_generar_factura(db: Session, asiento_data: dict, id_transaccion: int) -> Asiento:
    """
    Agrega un asiento a una transacción.
    Si la transacción es de tipo VENTA y NO tiene factura aún,
    genera automáticamente la factura.
    """

    # Obtener la transacción
    transaccion = get_transaccion(db, id_transaccion)

    if not transaccion:
        raise HTTPException(
            status_code=404,
            detail="Transacción no encontrada"
        )

    try:
        # Crear el asiento
        asiento_dict = asiento_data.copy() if isinstance(asiento_data, dict) else asiento_data.dict()
        asiento_dict["id_transaccion"] = id_transaccion

        db_asiento = Asiento(**asiento_dict)
        db.add(db_asiento)
        db.commit()
        db.refresh(db_asiento)

        # Si es VENTA → generar factura automática
        if transaccion.categoria == "VENTA":
            # Verificar si ya existe factura para esta transacción
            factura_existente = db.query(Factura).filter(
                Factura.id_transaccion == id_transaccion
            ).first()

            if not factura_existente:
                try:
                    factura = crear_factura_automatica(db, transaccion)
                except HTTPException as e:
                    # Si hay error al crear factura, no detener el proceso del asiento
                    print(f"Advertencia: {e.detail}")

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
# FUNCIÓN AUXILIAR: Generar factura manualmente si es necesario
# ---------------------------------------------------
def generar_factura_manual(db: Session, id_transaccion: int) -> Factura:
    """
    Genera manualmente una factura para una transacción de VENTA.
    Útil si la generación automática falló o quieres regenerar.
    """
    transaccion = get_transaccion(db, id_transaccion)

    if transaccion.categoria != "VENTA":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden generar facturas para transacciones de tipo VENTA"
        )

    return crear_factura_automatica(db, transaccion)


# ---------------------------------------------------
# RESTO DEL CÓDIGO SIN CAMBIOS
# ---------------------------------------------------

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
        tipo: Optional[str] = None,
        categoria: Optional[str] = None
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
    if categoria:
        query = query.filter(Transaccion.categoria == categoria)

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
    db.delete(transaccion)
    db.commit()
    return True