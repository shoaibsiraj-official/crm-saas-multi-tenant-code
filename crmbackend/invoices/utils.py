from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch


def generate_invoice_pdf(invoice):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)

    elements = []

    styles = getSampleStyleSheet()

    # =========================
    # Title
    # =========================

    elements.append(
        Paragraph(f"Invoice #{invoice.invoice_number}", styles["Heading1"])
    )

    elements.append(Spacer(1, 0.3 * inch))

    # =========================
    # Invoice Info
    # =========================

    elements.append(
        Paragraph(f"Client: {invoice.client.name}", styles["Normal"])
    )

    if invoice.project:
        elements.append(
            Paragraph(f"Project: {invoice.project.name}", styles["Normal"])
        )

    elements.append(
        Paragraph(f"Status: {invoice.status}", styles["Normal"])
    )

    elements.append(
        Paragraph(f"Due Date: {invoice.due_date}", styles["Normal"])
    )

    elements.append(Spacer(1, 0.3 * inch))

    # =========================
    # Items Table
    # =========================

    data = [
        ["Description", "Qty", "Price", "Subtotal"]
    ]

    for item in invoice.items.all():

        data.append([
            item.description,
            item.quantity,
            f"₹{item.price}",
            f"₹{item.subtotal}",
        ])

    table = Table(data)

    table.setStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('GRID', (0,0), (-1,-1), 1, colors.black),

        ('ALIGN', (1,1), (-1,-1), 'CENTER')
    ])

    elements.append(table)

    elements.append(Spacer(1, 0.4 * inch))

    # =========================
    # Total
    # =========================

    elements.append(
        Paragraph(f"Tax: ₹{invoice.tax}", styles["Normal"])
    )

    elements.append(
        Paragraph(f"<b>Total: ₹{invoice.total}</b>", styles["Heading3"])
    )

    # =========================
    # Build PDF
    # =========================

    doc.build(elements)

    buffer.seek(0)

    return buffer