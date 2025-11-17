"""
Rutas de API para el Libro Mayor.
Proporciona endpoints para generar el libro mayor con agrupación por cuentas mayores.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from BE.app.db import get_db
from BE.app.services.libro_mayor_service import (
    generar_libro_mayor_completo, 
    obtener_resumen_por_digitos
)
from BE.app.schemas.libro_mayor import LibroMayorResponse
from typing import Optional
from datetime import date

router = APIRouter(prefix="/api", tags=["Libro Mayor"])

@router.get("/libro_mayor", response_model=LibroMayorResponse)
def obtener_libro_mayor(
    digitos: int = Query(4, ge=1, le=10, description="Número de dígitos para agrupar cuentas mayores"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para filtrar transacciones"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin para filtrar transacciones"),
    incluir_detalle: bool = Query(False, description="Incluir subcuentas en el detalle"),
    db: Session = Depends(get_db)
):
    """
    Obtener el Libro Mayor agrupado por cuentas mayores.
    
    - **digitos**: Número de dígitos para determinar la cuenta mayor (ej: 4 → 1100 se agrupa como 1100)
    - **fecha_inicio**: Filtrar transacciones desde esta fecha (opcional)
    - **fecha_fin**: Filtrar transacciones hasta esta fecha (opcional) 
    - **incluir_detalle**: Si incluir el detalle de subcuentas para cada cuenta mayor
    
    Returns:
    ```json
    {
        "mayores": [
            {
                "codigo_mayor": "1100",
                "nombre_mayor": "Activo Circulante",
                "total_debe": 15000.00,
                "total_haber": 5000.00,
                "saldo": 10000.00,
                "subcuentas": [...]  // Solo si incluir_detalle=true
            }
        ],
        "resumen": {
            "total_cuentas": 5,
            "total_debe_general": 50000.00,
            "total_haber_general": 50000.00
        }
    }
    ```
    """
    try:
        resultado = generar_libro_mayor_completo(
            db=db,
            digitos=digitos,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            incluir_detalle=incluir_detalle
        )
        
        return resultado
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.get("/libro_mayor/resumen", response_model=LibroMayorResponse)
def obtener_resumen_libro_mayor(
    digitos: int = Query(4, ge=1, le=10, description="Número de dígitos para agrupar"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio"),
    fecha_fin: Optional[date] = Query(None, description="Fecha fin"),
    db: Session = Depends(get_db)
):
    """
    Obtener solo el resumen del Libro Mayor sin subcuentas.
    Endpoint optimizado para obtener solo los totales por cuenta mayor.
    """
    try:
        resultado = obtener_resumen_por_digitos(
            db=db,
            digitos=digitos,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        return resultado
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )