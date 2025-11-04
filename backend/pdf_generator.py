from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

def create_invoice_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    today = datetime.now().strftime("%d/%m/%Y")
    
    y = height - inch
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(inch, y, "FACTURE")
    y -= 0.5 * inch
    
    c.setFont("Helvetica", 10)
    invoice_num = data.get("invoice_number", "N/A")
    invoice_date = today
    due_date = data.get("due_date")
    
    c.drawString(inch, y, f"Numéro de facture: {invoice_num}")
    y -= 0.2 * inch
    c.drawString(inch, y, f"Date de facture: {invoice_date}")
    y -= 0.2 * inch
    c.drawString(inch, y, f"Date d'échéance: {due_date}")
    y -= 0.4 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "De:")
    y -= 0.2 * inch
    c.setFont("Helvetica", 10)
    
    seller = data.get("seller", {})
    if seller.get("name"):
        c.drawString(inch, y, seller.get("name", ""))
        y -= 0.15 * inch
    if seller.get("address"):
        c.drawString(inch, y, seller.get("address", ""))
        y -= 0.15 * inch
    if seller.get("phone"):
        c.drawString(inch, y, f"Téléphone: {seller.get('phone', '')}")
        y -= 0.15 * inch
    if seller.get("email"):
        c.drawString(inch, y, f"Courriel: {seller.get('email', '')}")
        y -= 0.3 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "À:")
    y -= 0.2 * inch
    c.setFont("Helvetica", 10)
    
    buyer = data.get("buyer", {})
    if buyer.get("name"):
        c.drawString(inch, y, buyer.get("name", ""))
        y -= 0.15 * inch
    if buyer.get("address"):
        c.drawString(inch, y, buyer.get("address", ""))
        y -= 0.15 * inch
    if buyer.get("phone"):
        c.drawString(inch, y, f"Téléphone: {buyer.get('phone', '')}")
        y -= 0.15 * inch
    if buyer.get("email"):
        c.drawString(inch, y, f"Courriel: {buyer.get('email', '')}")
        y -= 0.4 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(inch, y, "Articles:")
    y -= 0.3 * inch
    
    c.setFont("Helvetica-Bold", 9)
    c.drawString(inch, y, "Description")
    c.drawString(3.5 * inch, y, "Qté")
    c.drawString(4.5 * inch, y, "Prix")
    c.drawString(5.5 * inch, y, "Total")
    y -= 0.2 * inch
    
    c.setFont("Helvetica", 9)
    items = data.get("items", [])
    for item in items:
        desc = item.get("description", "")
        qty = item.get("quantity", 0)
        price = item.get("unit_price", 0)
        total = item.get("total", 0)
        
        c.drawString(inch, y, desc[:40])
        c.drawString(3.5 * inch, y, str(qty))
        c.drawString(4.5 * inch, y, f"${price:.2f}")
        c.drawString(5.5 * inch, y, f"${total:.2f}")
        y -= 0.2 * inch
    
    y -= 0.2 * inch
    c.setFont("Helvetica", 10)
    
    subtotal = data.get("subtotal", 0)
    tax_rate = data.get("tax_rate", 0)
    tax_amount = data.get("tax_amount", 0)
    total_amount = data.get("total_amount", 0)
    currency = data.get("currency", "USD")
    
    c.drawString(4.5 * inch, y, "Sous-total:")
    c.drawString(5.5 * inch, y, f"${subtotal:.2f}")
    y -= 0.2 * inch
    
    c.drawString(4.5 * inch, y, f"Taxe ({tax_rate}%):")
    c.drawString(5.5 * inch, y, f"${tax_amount:.2f}")
    y -= 0.2 * inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(4.5 * inch, y, "Total:")
    c.drawString(5.5 * inch, y, f"${total_amount:.2f} {currency}")
    y -= 0.4 * inch
    
    c.setFont("Helvetica", 9)
    notes = data.get("notes", "")
    payment_terms = data.get("payment_terms", "")
    
    if payment_terms:
        c.drawString(inch, y, f"Conditions de paiement: {payment_terms}")
        y -= 0.2 * inch
    
    if notes:
        c.drawString(inch, y, f"Notes: {notes}")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer
