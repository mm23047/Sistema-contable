"""
Rutas de API para operaciones de Facturas.
Proporciona endpoints CRUD y de descarga de facturas.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import  StreamingResponse
from sqlalchemy.orm import Session
from BE.app.db import get_db
from BE.app.models.factura_models import Factura
from BE.app.models.transaccion import Transaccion
from typing import List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

router = APIRouter(prefix="/api/facturas", tags=["Facturas"])


# =========================================================
# 🟦 LISTAR FACTURAS
# =========================================================
@router.get("/", response_model=List[dict])
def listar_facturas(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        id_transaccion: Optional[int] = Query(None),
        cliente: Optional[str] = Query(None),
        db: Session = Depends(get_db)
):
    """Obtener listado de facturas con filtros opcionales"""
    query = db.query(Factura)

    if id_transaccion:
        query = query.filter(Factura.id_transaccion == id_transaccion)

    if cliente:
        query = query.filter(Factura.cliente.ilike(f"%{cliente}%"))

    facturas = query.offset(skip).limit(limit).all()

    return [
        {
            "id_factura": str(f.id_factura),
            "numero_factura": f.numero_factura,
            "cliente": f.cliente,
            "monto_total": float(f.monto_total),
            "fecha_emision": f.fecha_emision.isoformat() if f.fecha_emision else None,
            "id_transaccion": f.id_transaccion,
            "estado": "Generada"
        }
        for f in facturas
    ]


# =========================================================
# 🟦 OBTENER FACTURA POR ID
# =========================================================
@router.get("/{factura_id}", response_model=dict)
def obtener_factura(
        factura_id: str,
        db: Session = Depends(get_db)
):
    """Obtener una factura específica por ID"""
    factura = db.query(Factura).filter(
        Factura.id_factura == factura_id
    ).first()

    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factura {factura_id} no encontrada"
        )

    # Obtener transacción asociada
    transaccion = db.query(Transaccion).filter(
        Transaccion.id_transaccion == factura.id_transaccion
    ).first()

    return {
        "id_factura": str(factura.id_factura),
        "numero_factura": factura.numero_factura,
        "cliente": factura.cliente,
        "monto_total": float(factura.monto_total),
        "fecha_emision": factura.fecha_emision.isoformat() if factura.fecha_emision else None,
        "id_transaccion": factura.id_transaccion,
        "categoria": transaccion.categoria if transaccion else None,
        "tipo": transaccion.tipo if transaccion else None,
        "estado": "Generada"
    }


# =========================================================
# 🟦 DESCARGAR FACTURA EN PDF
# =========================================================
@router.get("/{factura_id}/descargar-pdf")
def descargar_factura_pdf(
        factura_id: str,
        db: Session = Depends(get_db)
):
    """Descargar factura en formato PDF"""
    factura = db.query(Factura).filter(
        Factura.id_factura == factura_id
    ).first()

    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factura {factura_id} no encontrada"
        )

    # Crear PDF en memoria
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=1
    )
    title = Paragraph("FACTURA", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3 * inch))

    # Información de la factura
    info_data = [
        ["Número de Factura:", str(factura.numero_factura)],
        ["Fecha de Emisión:", factura.fecha_emision.strftime("%d/%m/%Y") if factura.fecha_emision else "N/A"],
        ["Cliente:", factura.cliente],
        ["Monto Total:", f"${float(factura.monto_total):,.2f}"]
    ]

    info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eef7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 0.5 * inch))

    # Totales
    totales_data = [
        ["CONCEPTO", "MONTO"],
        ["Monto Total", f"${float(factura.monto_total):,.2f}"]
    ]

    totales_table = Table(totales_data, colWidths=[3 * inch, 3 * inch])
    totales_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8eef7'))
    ]))

    elements.append(totales_table)

    # Generar PDF
    doc.build(elements)
    pdf_buffer.seek(0)

    # 👈 CAMBIO: Usar StreamingResponse en lugar de FileResponse
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Factura_{factura.numero_factura}.pdf"}
    )


# =========================================================
# 🟦 DESCARGAR FACTURA EN EXCEL
# =========================================================
@router.get("/{factura_id}/descargar-excel")
def descargar_factura_excel(
        factura_id: str,
        db: Session = Depends(get_db)
):
    """Descargar factura en formato Excel"""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="openpyxl no está instalado. Instala con: pip install openpyxl"
        )

    factura = db.query(Factura).filter(
        Factura.id_factura == factura_id
    ).first()

    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Factura {factura_id} no encontrada"
        )

    # Crear workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Factura"

    # Título
    ws['A1'] = "FACTURA"
    ws['A1'].font = Font(size=16, bold=True, color="FFFFFF")
    ws['A1'].fill = PatternFill(start_color="1f4788", end_color="1f4788", fill_type="solid")
    ws.merge_cells('A1:D1')
    ws['A1'].alignment = Alignment(horizontal='center', vertical='center')

    # Datos
    ws['A3'] = "Número de Factura:"
    ws['B3'] = factura.numero_factura
    ws['A4'] = "Fecha de Emisión:"
    ws['B4'] = factura.fecha_emision.strftime("%d/%m/%Y") if factura.fecha_emision else "N/A"
    ws['A5'] = "Cliente:"
    ws['B5'] = factura.cliente
    ws['A6'] = "Monto Total:"
    ws['B6'] = float(factura.monto_total)
    ws['B6'].number_format = '$#,##0.00'

    # Ajustar anchos
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 25

    # Guardar en memoria
    excel_buffer = io.BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)

    # 👈 CAMBIO: Usar StreamingResponse en lugar de FileResponse
    return StreamingResponse(
        iter([excel_buffer.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=Factura_{factura.numero_factura}.xlsx"}
    )