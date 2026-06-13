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
from store.models import Order

def admin_invoice(request, order_id):
    """Generates an invoice view for the admin dashboard."""
    order = get_object_or_404(Order, id=order_id)
    
    # A simple placeholder response so the button doesn't crash
    return HttpResponse(f"<h1>Invoice for Order #{order.id}</h1><p>Invoice generation system coming soon!</p>")

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