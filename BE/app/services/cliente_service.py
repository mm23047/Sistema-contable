"""
Servicio de gestión de clientes.
Lógica de negocio para CRUD de clientes.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from fastapi import HTTPException, status
from typing import Optional, List

from BE.app.models.cliente import Cliente
from BE.app.schemas.cliente_schemas import ClienteCreate, ClienteUpdate


# =========================================================
# 🟦 CREAR CLIENTE
# =========================================================
def crear_cliente(db: Session, cliente_data: ClienteCreate) -> Cliente:
    """
    Crea un nuevo cliente.
    Valida que no exista duplicado por NIT.
    """
    # Validar NIT único si se proporciona
    if cliente_data.nit:
        cliente_existente = db.query(Cliente).filter(
            Cliente.nit == cliente_data.nit
        ).first()
        
        if cliente_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un cliente con NIT {cliente_data.nit}"
            )
    
    # Crear cliente
    nuevo_cliente = Cliente(
        nombre=cliente_data.nombre,
        nit=cliente_data.nit,
        direccion=cliente_data.direccion,
        telefono=cliente_data.telefono,
        email=cliente_data.email,
        tipo_cliente=cliente_data.tipo_cliente,
        notas=cliente_data.notas
    )
    
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    
    return nuevo_cliente


# =========================================================
# 🟦 OBTENER CLIENTE POR ID
# =========================================================
def obtener_cliente_por_id(db: Session, cliente_id: int) -> Cliente:
    """Obtiene un cliente por su ID"""
    cliente = db.query(Cliente).filter(
        Cliente.id_cliente == cliente_id
    ).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {cliente_id} no encontrado"
        )
    
    return cliente


# =========================================================
# 🟦 LISTAR CLIENTES
# =========================================================
def listar_clientes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    busqueda: Optional[str] = None,
    tipo: Optional[str] = None,
    activo: Optional[str] = None
) -> List[Cliente]:
    """
    Lista clientes con filtros opcionales.
    busqueda: busca en nombre, NIT, email
    tipo: INDIVIDUAL o EMPRESA
    activo: SI o NO
    """
    query = db.query(Cliente)
    
    # Filtro de búsqueda general
    if busqueda:
        busqueda_pattern = f"%{busqueda}%"
        query = query.filter(
            or_(
                Cliente.nombre.ilike(busqueda_pattern),
                Cliente.nit.ilike(busqueda_pattern),
                Cliente.email.ilike(busqueda_pattern)
            )
        )
    
    # Filtro por tipo
    if tipo and tipo in ['INDIVIDUAL', 'EMPRESA']:
        query = query.filter(Cliente.tipo_cliente == tipo)
    
    # Filtro por estado activo
    if activo and activo in ['SI', 'NO']:
        query = query.filter(Cliente.activo == activo)
    
    return query.order_by(Cliente.nombre).offset(skip).limit(limit).all()


# =========================================================
# 🟦 ACTUALIZAR CLIENTE
# =========================================================
def actualizar_cliente(
    db: Session,
    cliente_id: int,
    cliente_update: ClienteUpdate
) -> Cliente:
    """Actualiza un cliente existente"""
    cliente = obtener_cliente_por_id(db, cliente_id)
    
    # Validar NIT único si se está actualizando
    if cliente_update.nit and cliente_update.nit != cliente.nit:
        cliente_existente = db.query(Cliente).filter(
            Cliente.nit == cliente_update.nit,
            Cliente.id_cliente != cliente_id
        ).first()
        
        if cliente_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro cliente con NIT {cliente_update.nit}"
            )
    
    # Actualizar campos proporcionados
    update_data = cliente_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cliente, field, value)
    
    db.commit()
    db.refresh(cliente)
    
    return cliente


# =========================================================
# 🟦 ELIMINAR/DESACTIVAR CLIENTE
# =========================================================
def desactivar_cliente(db: Session, cliente_id: int) -> Cliente:
    """
    Desactiva un cliente (no lo elimina físicamente).
    Mejor práctica: marcar como inactivo en lugar de eliminar.
    """
    cliente = obtener_cliente_por_id(db, cliente_id)
    cliente.activo = "NO"
    
    db.commit()
    db.refresh(cliente)
    
    return cliente


def eliminar_cliente(db: Session, cliente_id: int) -> bool:
    """
    Elimina físicamente un cliente.
    Solo permitido si no tiene facturas asociadas.
    """
    cliente = obtener_cliente_por_id(db, cliente_id)
    
    # Verificar que no tenga facturas
    from BE.app.models.factura_models import Factura
    facturas_count = db.query(func.count(Factura.id_factura)).filter(
        Factura.id_cliente == cliente_id
    ).scalar()
    
    if facturas_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el cliente porque tiene {facturas_count} factura(s) asociada(s). Use desactivar en su lugar."
        )
    
    db.delete(cliente)
    db.commit()
    
    return True


# =========================================================
# 🟦 BUSCAR CLIENTE POR NIT
# =========================================================
def buscar_cliente_por_nit(db: Session, nit: str) -> Optional[Cliente]:
    """Busca un cliente por su NIT"""
    return db.query(Cliente).filter(Cliente.nit == nit).first()


# =========================================================
# 🟦 ESTADÍSTICAS DE CLIENTES
# =========================================================
def obtener_estadisticas_clientes(db: Session):
    """Obtiene estadísticas generales de clientes"""
    total = db.query(func.count(Cliente.id_cliente)).scalar()
    activos = db.query(func.count(Cliente.id_cliente)).filter(Cliente.activo == "SI").scalar()
    individuales = db.query(func.count(Cliente.id_cliente)).filter(Cliente.tipo_cliente == "INDIVIDUAL").scalar()
    empresas = db.query(func.count(Cliente.id_cliente)).filter(Cliente.tipo_cliente == "EMPRESA").scalar()
    
    return {
        "total_clientes": total,
        "activos": activos,
        "inactivos": total - activos,
        "individuales": individuales,
        "empresas": empresas
    }
