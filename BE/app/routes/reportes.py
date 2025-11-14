"""
Rutas de API para operaciones de Reportes.
Proporciona endpoints para generar reportes contables y exportaciones.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from BE.app.db import get_db
from BE.app.services.reporte_service import (
    generar_libro_diario, generar_export_excel, generar_export_html, generar_balance
)
from typing import Optional
from io import StringIO, BytesIO

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])

@router.get("/libro-diario")
def obtener_libro_diario(
    periodo_id: Optional[int] = Query(None, description="Filtrar por ID de período"),
    db: Session = Depends(get_db)
):
    """Obtener el Libro Diario como JSON"""
    return generar_libro_diario(db, periodo_id)

@router.get("/libro-diario/export")
def exportar_libro_diario(
    format: str = Query(..., pattern="^(excel|html)$", description="Export format: excel or html"),
    periodo_id: Optional[int] = Query(None, description="Filter by period ID"),
    db: Session = Depends(get_db)
):
    """Exportar el Libro Diario en formato Excel o HTML"""
    
    if format == "excel":
        # Generate Excel file
        buffer = generar_export_excel(db, periodo_id)
        
        # Return file as download
        return StreamingResponse(
            BytesIO(buffer.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=libro_diario.xlsx"}
        )
    
    elif format == "html":
        # Generate HTML file
        html_content = generar_export_html(db, periodo_id)
        
        # Return HTML file as download - Convert string to BytesIO for proper streaming
        return StreamingResponse(
            BytesIO(html_content.encode('utf-8')),
            media_type="text/html",
            headers={"Content-Disposition": "attachment; filename=libro_diario.html"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Use 'excel' or 'html'"
        )

@router.get("/balance")
def obtener_balance(
    periodo_id: int = Query(..., description="Period ID for balance calculation"),
    db: Session = Depends(get_db)
):
    """Obtener resumen de balance por cuenta para un período específico"""
    # TODO: Implementar cálculo detallado de balance y validación
    return generar_balance(db, periodo_id)