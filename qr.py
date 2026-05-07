import os
import qrcode
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# =========================================================
# QR CODE GENERATOR
# =========================================================
def generate_qr(name, total):
    """
    Generate QR image for payment
    """

    os.makedirs("static", exist_ok=True)

    # QR payment text
    qr_data = f"""
    Luxe Restaurant
    Customer: {name}
    Amount: RM {total}
    Thank you!
    """

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    path = "static/payment_qr.png"

    img.save(path)

    return path


# =========================================================
# PDF RECEIPT GENERATOR
# =========================================================
def generate_pdf(name, phone, address, table_no,
                 order_type, payment, items, total):

    os.makedirs("static", exist_ok=True)

    file_path = f"static/receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    c = canvas.Canvas(file_path, pagesize=letter)

    y = 750

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(180, y, "LUXE RESTAURANT")

    y -= 40
    c.setFont("Helvetica", 12)

    lines = [
        f"Name: {name}",
        f"Phone: {phone}",
        f"Address: {address}",
        f"Table No: {table_no}",
        f"Order Type: {order_type}",
        f"Payment: {payment}",
        f"Items: {items}",
        f"Total: RM {total}",
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ]

    for line in lines:
        c.drawString(50, y, line)
        y -= 25

    # Generate QR
    qr_path = generate_qr(name, total)

    # Insert QR into PDF
    c.drawImage(qr_path, 400, 500, width=120, height=120)

    c.save()

    return file_path
