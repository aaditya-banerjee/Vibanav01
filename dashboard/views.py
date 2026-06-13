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


def invoice_pdf(request, order_id):
    """Generates a downloadable PDF invoice for the admin dashboard."""
    order = get_object_or_404(Order, id=order_id)
    
    # 1. Grab the HTML template we just made
    template_path = 'dashboard/invoice_pdf.html'
    context = {'order': order}
    template = get_template(template_path)
    html = template.render(context)
    
    # 2. Tell the browser we are sending a PDF, not a webpage
    response = HttpResponse(content_type='application/pdf')
    # Use 'attachment' to force a download, or 'inline' to view in browser
    response['Content-Disposition'] = f'attachment; filename="Vibana_Invoice_{order.id}.pdf"'
    
    # 3. Let xhtml2pdf convert the HTML string into a PDF document
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # 4. Error handling
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