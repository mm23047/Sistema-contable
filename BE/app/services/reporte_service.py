"""
Capa de servicios para operaciones de Reportes.
Maneja la lógica de negocio para generar reportes contables.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from BE.app.models.asiento import Asiento
from BE.app.models.transaccion import Transaccion
from BE.app.models.catalogo_cuentas import CatalogoCuentas
from BE.app.models.periodo import PeriodoContable
from typing import List, Dict, Any, Optional
import pandas as pd
from io import BytesIO

def generar_libro_diario(db: Session, periodo_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Generar el reporte del Libro Diario.
    Retorna una lista de asientos contables con detalles de transacciones y cuentas.
    """
    query = db.query(
        Asiento.id_asiento,
        Asiento.debe,
        Asiento.haber,
        Transaccion.id_transaccion,
        Transaccion.fecha_transaccion,
        Transaccion.descripcion,
        Transaccion.tipo,
        CatalogoCuentas.codigo_cuenta,
        CatalogoCuentas.nombre_cuenta,
        CatalogoCuentas.tipo_cuenta
    ).join(
        Transaccion, Asiento.id_transaccion == Transaccion.id_transaccion
    ).join(
        CatalogoCuentas, Asiento.id_cuenta == CatalogoCuentas.id_cuenta
    )
    
    # Filter by period if specified
    if periodo_id:
        query = query.filter(Transaccion.id_periodo == periodo_id)
    
    # Order by transaction date and entry ID
    query = query.order_by(Transaccion.fecha_transaccion, Asiento.id_asiento)
    
    results = query.all()
    
    # Convert to list of dictionaries
    libro_diario = []
    for row in results:
        libro_diario.append({
            "id_asiento": row.id_asiento,
            "id_transaccion": row.id_transaccion,
            "fecha_transaccion": row.fecha_transaccion.isoformat(),
            "descripcion": row.descripcion,
            "tipo_transaccion": row.tipo,
            "codigo_cuenta": row.codigo_cuenta,
            "nombre_cuenta": row.nombre_cuenta,
            "tipo_cuenta": row.tipo_cuenta,
            "debe": float(row.debe),
            "haber": float(row.haber)
        })
    
    return libro_diario

def generar_export_excel(db: Session, periodo_id: Optional[int] = None) -> BytesIO:
    """
    Generate Excel export of the General Journal.
    Returns BytesIO buffer with Excel file content.
    """
    # TODO: Implementar formato detallado de Excel
    data = generar_libro_diario(db, periodo_id)
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Libro Diario', index=False)
        
        # TODO: Añadir formato, encabezados, totales, etc.
        
    buffer.seek(0)
    return buffer

def generar_export_html(db: Session, periodo_id: Optional[int] = None) -> str:
    """
    Generate HTML export of the General Journal.
    Returns HTML string with formatted table.
    """
    # TODO: Implementar formato detallado de HTML con CSS
    data = generar_libro_diario(db, periodo_id)
    df = pd.DataFrame(data)
    
    html = df.to_html(classes='table table-striped', table_id='libro-diario')
    
    # Wrap in basic HTML structure
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Libro Diario</title>
        <style>
            .table {{ border-collapse: collapse; width: 100%; }}
            .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            .table th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>Libro Diario</h1>
        {html}
    </body>
    </html>
    """
    
    return full_html

def generar_balance(db: Session, periodo_id: int) -> Dict[str, Any]:
    """
    Generate a balance summary by account for a specific period.
    Returns summary of debits and credits by account.
    """
    # TODO: Implementar cálculo detallado de balance
    query = db.query(
        CatalogoCuentas.codigo_cuenta,
        CatalogoCuentas.nombre_cuenta,
        CatalogoCuentas.tipo_cuenta,
        func.sum(Asiento.debe).label('total_debe'),
        func.sum(Asiento.haber).label('total_haber')
    ).join(
        Asiento, CatalogoCuentas.id_cuenta == Asiento.id_cuenta
    ).join(
        Transaccion, Asiento.id_transaccion == Transaccion.id_transaccion
    ).filter(
        Transaccion.id_periodo == periodo_id
    ).group_by(
        CatalogoCuentas.id_cuenta,
        CatalogoCuentas.codigo_cuenta,
        CatalogoCuentas.nombre_cuenta,
        CatalogoCuentas.tipo_cuenta
    ).all()
    
    balance = {
        "periodo_id": periodo_id,
        "cuentas": [],
        "totales": {
            "total_debe": 0.0,
            "total_haber": 0.0
        }
    }
    
    for row in query:
        cuenta_balance = {
            "codigo_cuenta": row.codigo_cuenta,
            "nombre_cuenta": row.nombre_cuenta,
            "tipo_cuenta": row.tipo_cuenta,
            "total_debe": float(row.total_debe or 0),
            "total_haber": float(row.total_haber or 0),
            "saldo": float((row.total_debe or 0) - (row.total_haber or 0))
        }
        balance["cuentas"].append(cuenta_balance)
        balance["totales"]["total_debe"] += cuenta_balance["total_debe"]
        balance["totales"]["total_haber"] += cuenta_balance["total_haber"]
    
    return balance