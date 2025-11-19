"""
Rutas de API para operaciones de Clientes.
Proporciona endpoints CRUD para gestión de clientes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from BE.app.db import get_db
from BE.app.schemas.cliente_schemas import ClienteCreate, ClienteUpdate, ClienteOut, ClienteResumen
from BE.app.services.cliente_service import (
    crear_cliente,
    obtener_cliente_por_id,
    listar_clientes,
    actualizar_cliente,
    desactivar_cliente,
    eliminar_cliente,
    buscar_cliente_por_nit,
    obtener_estadisticas_clientes
)

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])


# =========================================================
# 🟦 CREAR CLIENTE
# =========================================================
@router.post("/", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
def crear_nuevo_cliente(
    cliente: ClienteCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo cliente.
    - Valida NIT único
    - Tipo: INDIVIDUAL o EMPRESA
    """
    return crear_cliente(db, cliente)


# =========================================================
# 🟦 LISTAR CLIENTES
# =========================================================
@router.get("/", response_model=List[ClienteResumen])
def listar_todos_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    busqueda: Optional[str] = Query(None, description="Buscar en nombre, NIT o email"),
    tipo: Optional[str] = Query(None, description="INDIVIDUAL o EMPRESA"),
    activo: Optional[str] = Query(None, description="SI o NO"),
    db: Session = Depends(get_db)
):
    """
    Lista clientes con filtros opcionales.
    - busqueda: busca en nombre, NIT y email
    - tipo: filtra por INDIVIDUAL o EMPRESA
    - activo: filtra por SI o NO
    """
    return listar_clientes(db, skip, limit, busqueda, tipo, activo)


# =========================================================
# 🟦 OBTENER CLIENTE POR ID
# =========================================================
@router.get("/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene un cliente específico por ID"""
    return obtener_cliente_por_id(db, cliente_id)


# =========================================================
# 🟦 BUSCAR CLIENTE POR NIT
# =========================================================
@router.get("/buscar/nit/{nit}", response_model=ClienteOut)
def buscar_por_nit(
    nit: str,
    db: Session = Depends(get_db)
):
    """Busca un cliente por su NIT"""
    cliente = buscar_cliente_por_nit(db, nit)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró cliente con NIT {nit}"
        )
    return cliente


# =========================================================
# 🟦 ACTUALIZAR CLIENTE
# =========================================================
@router.put("/{cliente_id}", response_model=ClienteOut)
def actualizar_cliente_existente(
    cliente_id: int,
    cliente: ClienteUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza los datos de un cliente"""
    return actualizar_cliente(db, cliente_id, cliente)


# =========================================================
# 🟦 DESACTIVAR CLIENTE
# =========================================================
@router.patch("/{cliente_id}/desactivar", response_model=ClienteOut)
def desactivar_cliente_existente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """
    Desactiva un cliente (marca como inactivo).
    Mejor práctica que eliminarlo.
    """
    return desactivar_cliente(db, cliente_id)


# =========================================================
# 🟦 ELIMINAR CLIENTE
# =========================================================
@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente_existente(
    cliente_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un cliente físicamente.
    Solo permitido si no tiene facturas asociadas.
    """
    eliminar_cliente(db, cliente_id)
    return None


# =========================================================
# 🟦 ESTADÍSTICAS DE CLIENTES
# =========================================================
@router.get("/estadisticas/resumen")
def obtener_estadisticas(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas generales de clientes.
    - Total, activos, inactivos
    - Individuales vs empresas
    """
    return obtener_estadisticas_clientes(db)
