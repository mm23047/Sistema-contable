"""
Rutas de API para operaciones del Catálogo de Cuentas.
Proporciona endpoints CRUD para gestionar el catálogo de cuentas.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from BE.app.db import get_db
from BE.app.schemas.catalogo_cuentas import CatalogoCuentaCreate, CatalogoCuentaRead, CatalogoCuentaUpdate
from BE.app.services.catalogo_service import (
    create_cuenta, get_cuenta, get_cuentas, update_cuenta, delete_cuenta
)
from typing import List

router = APIRouter(prefix="/api/catalogo-cuentas", tags=["Catalogo de Cuentas"])

@router.post("/", response_model=CatalogoCuentaRead, status_code=status.HTTP_201_CREATED)
def crear_cuenta(cuenta: CatalogoCuentaCreate, db: Session = Depends(get_db)):
    """Crear una nueva cuenta en el catálogo de cuentas"""
    return create_cuenta(db, cuenta)

@router.get("/", response_model=List[CatalogoCuentaRead])
def listar_cuentas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtener todas las cuentas con paginación"""
    return get_cuentas(db, skip=skip, limit=limit)

@router.get("/{cuenta_id}", response_model=CatalogoCuentaRead)
def obtener_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    """Obtener una cuenta específica por ID"""
    return get_cuenta(db, cuenta_id)

@router.put("/{cuenta_id}", response_model=CatalogoCuentaRead)
def actualizar_cuenta(cuenta_id: int, cuenta: CatalogoCuentaUpdate, db: Session = Depends(get_db)):
    """Actualizar una cuenta existente"""
    return update_cuenta(db, cuenta_id, cuenta)

@router.delete("/{cuenta_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cuenta(cuenta_id: int, db: Session = Depends(get_db)):
    """Eliminar una cuenta"""
    delete_cuenta(db, cuenta_id)
    return None