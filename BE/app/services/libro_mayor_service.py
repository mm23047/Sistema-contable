"""
Servicio para generar el Libro Mayor.
Contiene la lógica de negocio para calcular saldos y agrupar por cuentas mayores.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models.asiento import Asiento
from app.models.catalogo_cuentas import CatalogoCuentas
from app.models.transaccion import Transaccion
from typing import Optional, Dict, List, Any
from datetime import date
from decimal import Decimal
import logging

# Configurar logger
logger = logging.getLogger(__name__)

def generar_libro_mayor_completo(
    db: Session,
    digitos: int,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    incluir_detalle: bool = False
) -> Dict[str, Any]:
    """
    Generar el libro mayor completo con agrupación por cuentas mayores.
    
    Args:
        db: Sesión de base de datos
        digitos: Número de dígitos para determinar cuenta mayor
        fecha_inicio: Fecha de inicio para filtrar
        fecha_fin: Fecha fin para filtrar
        incluir_detalle: Si incluir subcuentas detalladas
    
    Returns:
        Diccionario con mayores, subcuentas (si se solicita) y resumen
    """
    # Validar parámetros de entrada
    validar_parametros_libro_mayor(digitos, fecha_inicio, fecha_fin)
    
    logger.info(f"Generando libro mayor: dígitos={digitos}, fecha_inicio={fecha_inicio}, fecha_fin={fecha_fin}")
    
    try:
        # Construir query optimizada con OUTER JOIN para incluir cuentas sin movimientos
        query = db.query(
            CatalogoCuentas.codigo_cuenta,
            CatalogoCuentas.nombre_cuenta,
            CatalogoCuentas.tipo_cuenta,
            func.coalesce(func.sum(Asiento.debe), Decimal('0')).label('total_debe'),
            func.coalesce(func.sum(Asiento.haber), Decimal('0')).label('total_haber')
        ).select_from(CatalogoCuentas).outerjoin(
            Asiento, Asiento.id_cuenta == CatalogoCuentas.id_cuenta
        ).outerjoin(
            Transaccion, Transaccion.id_transaccion == Asiento.id_transaccion
        )
    
        # Aplicar filtros de fecha - manejar NULLs correctamente en OUTER JOIN
        if fecha_inicio:
            query = query.filter(
                or_(
                    Transaccion.fecha_transaccion.is_(None),
                    func.date(Transaccion.fecha_transaccion) >= fecha_inicio
                )
            )
        if fecha_fin:
            query = query.filter(
                or_(
                    Transaccion.fecha_transaccion.is_(None),
                    func.date(Transaccion.fecha_transaccion) <= fecha_fin
                )
            )
    
        # Agrupar por cuenta y obtener totales
        query = query.group_by(
            CatalogoCuentas.codigo_cuenta,
            CatalogoCuentas.nombre_cuenta,
            CatalogoCuentas.tipo_cuenta
        )
        
        # Ejecutar query
        resultados_cuentas = query.all()
        logger.debug(f"Encontradas {len(resultados_cuentas)} cuentas")
    
        # Procesar resultados y agrupar por cuenta mayor
        mayores_dict: Dict[str, Dict[str, Any]] = {}
        
        for cuenta in resultados_cuentas:
            # Determinar código de cuenta mayor según dígitos (tomar exactamente N dígitos)
            codigo_completo = cuenta.codigo_cuenta
            if len(codigo_completo) >= digitos:
                codigo_mayor = codigo_completo[:digitos]
            else:
                codigo_mayor = codigo_completo.ljust(digitos, '0')
            
            # Mantener precisión decimal para cálculos contables
            debe = Decimal(str(cuenta.total_debe or 0))
            haber = Decimal(str(cuenta.total_haber or 0))
            saldo_cuenta = debe - haber  # Saldo real (puede ser negativo)
            
            # Si la cuenta mayor no existe, crearla
            if codigo_mayor not in mayores_dict:
                # Obtener nombre de cuenta mayor (buscar cuenta que coincida exactamente)
                cuenta_mayor = db.query(CatalogoCuentas).filter(
                    CatalogoCuentas.codigo_cuenta == codigo_mayor
                ).first()
                
                nombre_mayor = cuenta_mayor.nombre_cuenta if cuenta_mayor else f"Cuenta Mayor {codigo_mayor}"
                
                mayores_dict[codigo_mayor] = {
                    "codigo_mayor": codigo_mayor,
                    "nombre_mayor": nombre_mayor,
                    "total_debe": Decimal('0'),
                    "total_haber": Decimal('0'),
                    "saldo": Decimal('0'),
                    "subcuentas": []
                }
            
            # Sumar totales a la cuenta mayor (manteniendo precisión)
            mayores_dict[codigo_mayor]["total_debe"] += debe
            mayores_dict[codigo_mayor]["total_haber"] += haber
            mayores_dict[codigo_mayor]["saldo"] += saldo_cuenta
            
            # Si se solicita detalle, agregar subcuenta
            if incluir_detalle:
                subcuenta = {
                    "codigo_cuenta": cuenta.codigo_cuenta,
                    "nombre_cuenta": cuenta.nombre_cuenta,
                    "tipo_cuenta": cuenta.tipo_cuenta,
                    "total_debe": float(debe),  # Convertir a float solo para JSON
                    "total_haber": float(haber),
                    "saldo": float(saldo_cuenta)
                }
                mayores_dict[codigo_mayor]["subcuentas"].append(subcuenta)
        
        # Convertir a float para JSON y preparar respuesta
        mayores_lista = []
        total_debe_acumulado = Decimal('0')
        total_haber_acumulado = Decimal('0')
        
        for codigo in sorted(mayores_dict.keys()):
            mayor = mayores_dict[codigo]
            
            # Acumular totales con precisión
            total_debe_acumulado += mayor["total_debe"]
            total_haber_acumulado += mayor["total_haber"]
            
            # Convertir a float para respuesta JSON
            mayor_json = {
                "codigo_mayor": mayor["codigo_mayor"],
                "nombre_mayor": mayor["nombre_mayor"],
                "total_debe": float(mayor["total_debe"]),
                "total_haber": float(mayor["total_haber"]),
                "saldo": float(mayor["saldo"]),
                "subcuentas": sorted(mayor["subcuentas"], key=lambda x: x["codigo_cuenta"]) if incluir_detalle else []
            }
            mayores_lista.append(mayor_json)
        
        # Calcular resumen con precisión decimal
        total_debe_general = float(total_debe_acumulado)
        total_haber_general = float(total_haber_acumulado)
        
        resumen = {
            "total_cuentas": len(mayores_lista),
            "total_debe_general": total_debe_general,
            "total_haber_general": total_haber_general,
            "diferencia": abs(total_debe_general - total_haber_general),
            "fecha_generacion": date.today().isoformat()
        }
        
        logger.info(f"Libro mayor generado exitosamente: {len(mayores_lista)} cuentas mayores")
        
        return {
            "mayores": mayores_lista,
            "resumen": resumen,
            "filtros_aplicados": {
                "digitos": digitos,
                "fecha_inicio": fecha_inicio.isoformat() if fecha_inicio else None,
                "fecha_fin": fecha_fin.isoformat() if fecha_fin else None,
                "incluir_detalle": incluir_detalle
            }
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al generar libro mayor: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error de base de datos: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Error generando libro mayor: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

def obtener_resumen_por_digitos(
    db: Session,
    digitos: int,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None
) -> Dict[str, Any]:
    """
    Obtener solo el resumen por cuentas mayores sin detalle de subcuentas.
    Versión optimizada para consultas rápidas.
    """
    return generar_libro_mayor_completo(
        db=db,
        digitos=digitos,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        incluir_detalle=False
    )

def validar_parametros_libro_mayor(
    digitos: int,
    fecha_inicio: Optional[date],
    fecha_fin: Optional[date]
) -> None:
    """
    Validar los parámetros de entrada para el libro mayor.
    
    Raises:
        ValueError: Si algún parámetro es inválido
    """
    if digitos < 1 or digitos > 10:
        raise ValueError("El número de dígitos debe estar entre 1 y 10")
    
    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        raise ValueError("La fecha de inicio no puede ser posterior a la fecha fin")
    
    # Validar que las fechas no sean futuras
    hoy = date.today()
    if fecha_inicio and fecha_inicio > hoy:
        raise ValueError("La fecha de inicio no puede ser futura")
    
    if fecha_fin and fecha_fin > hoy:
        raise ValueError("La fecha fin no puede ser futura")