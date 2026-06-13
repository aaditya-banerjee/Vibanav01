# dashboard/views.py
from django.http import FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from store.models import Order
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template


def invoice_pdf(request, order_id, tax_type):
    """Generates an itemized, GST-compliant PDF invoice."""
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    
    # 1. Calculate Total Quantity
    total_quantity = sum(item.quantity for item in items)
    
    # 2. Financials & GST Logic
    subtotal = float(order.total_amount) # Base price from the portal
    gst_rate = 0
    cgst_amount = 0.00
    sgst_amount = 0.00
    
    if tax_type == 'gst':
        # Apply the Vibana Tax Brackets
        gst_rate = 18 if total_quantity >= 3 else 5
        
        # Split tax evenly between CGST and SGST
        total_tax_amount = subtotal * (gst_rate / 100.0)
        cgst_amount = total_tax_amount / 2
        sgst_amount = total_tax_amount / 2
        
    grand_total = subtotal + cgst_amount + sgst_amount
    
    context = {
        'order': order,
        'items': items,
        'tax_type': tax_type,
        'total_quantity': total_quantity,
        'subtotal': f"{subtotal:,.2f}",
        'gst_rate': gst_rate,
        'cgst_amount': f"{cgst_amount:,.2f}",
        'sgst_amount': f"{sgst_amount:,.2f}",
        'grand_total': f"{grand_total:,.2f}",
    }
    
    template = get_template('dashboard/invoice_pdf.html')
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Vibana_Invoice_{order.id}_{tax_type}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors generating the PDF.', status=500)
    return response

@staff_member_required
def generate_invoice_pdf(request, order_id):
    # Retrieve the specific order
    order = get_object_or_404(Order, id=order_id)
    
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # --- Draw the PDF Content ---
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "THREADS CO. - OFFICIAL INVOICE")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, 720, f"Order Number: #{order.id}")
    p.drawString(50, 700, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    customer_name = order.customer.username if order.customer else "Guest Customer"
    p.drawString(50, 680, f"Customer: {customer_name}")
    p.drawString(50, 660, f"Order Status: {order.status}")
    
    # Draw a line separator
    p.line(50, 640, 550, 640)
    
    # Financials
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 610, f"Grand Total: ${order.total_amount}")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, 100, "Thank you for your business!")
    
    # Close the PDF object cleanly
    p.showPage()
    p.save()
    
    # File buffer needs to be reset to the beginning before reading
    buffer.seek(0)
    
    # Return the buffer as a downloadable file response
    return FileResponse(buffer, as_attachment=True, filename=f'invoice_{order.id}.pdf')