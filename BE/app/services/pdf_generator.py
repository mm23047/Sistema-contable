from io import BytesIO
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm

# =====================================================
# 🟢 FASE 1: PDF NORMAL (Tu versión original)
# =====================================================



# =====================================================
# 🟢 FASE 7: PDF ESTILO FISCAL (NUEVO)
# =====================================================
def generar_pdf_factura_fiscal(factura, asientos):
    """
    Genera un PDF estilo factura fiscal:
        ✔ Encabezado profesional
        ✔ Tabla de líneas
        ✔ Totales con IVA
        ✔ Formato limpio y formal
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    elements = []

    # -----------------------------------------------------
    # Encabezado fiscal
    # -----------------------------------------------------
    elements.append(Paragraph("<b>FACTURA FISCAL</b>", styles["Title"]))
    elements.append(Spacer(1, 6))

    # Datos de factura
    elements.append(Paragraph(f"<b>N° Factura:</b> {factura.numero_factura}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Cliente:</b> {factura.cliente}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Fecha de Emisión:</b> {factura.fecha_emision}", styles["Normal"]))
    elements.append(Paragraph(f"<b>ID Transacción:</b> {factura.id_transaccion}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # -----------------------------------------------------
    # Construcción de tabla fiscal
    # -----------------------------------------------------
    data = [["Cuenta", "Tipo Movimiento", "Monto"]]  # encabezados

    subtotal = 0

    for a in asientos:
        monto = float(a.monto)
        subtotal += monto

        data.append([
            a.cuenta_codigo,
            a.tipo_movimiento,
            f"${monto:,.2f}"
        ])

    # Totales Fiscales
    IVA = subtotal * 0.13
    TOTAL = subtotal + IVA

    data.append(["", "", ""])
    data.append(["SUBTOTAL", "", f"${subtotal:,.2f}"])
    data.append(["IVA (13%)", "", f"${IVA:,.2f}"])
    data.append(["TOTAL A PAGAR", "", f"${TOTAL:,.2f}"])

    # Estilo de tabla fiscal
    tabla = Table(data, colWidths=[80*mm, 50*mm, 40*mm])

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightgrey),
        ("FONTNAME", (0, -3), (-1, -1), "Helvetica-Bold"),
    ]))

    elements.append(tabla)
    elements.append(Spacer(1, 20))

    # -----------------------------------------------------
    # Pie de página fiscal
    # -----------------------------------------------------
    elements.append(Paragraph(
        "<i>Documento generado automáticamente. Válido como comprobante fiscal.</i>",
        styles["Italic"]
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
