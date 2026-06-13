from django.contrib import admin
from django.utils.html import format_html
from store.models import Product, Category, Order, Invoice
from django.urls import reverse


# 1. Customize the Global Dashboard Branding
admin.site.site_header = "Threads Co. Administration"
admin.site.site_title = "Threads Admin Portal"
admin.site.index_title = "Welcome to the Staff CRM Workspace"

# 2. Inventory Control Panel
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Columns to display in the data grid
    list_display = ('name', 'image_tag', 'category', 'size', 'color', 'price', 'stock_quantity', 'inventory_alert')
    
    # Sidebar filters
    list_filter = ('category', 'size', 'color')
    
    # Search bar targets
    search_fields = ('name', 'description')
    
    # Allow staff to update pricing and stock directly from the grid view
    list_editable = ('price', 'stock_quantity') 

    # Custom column for visual stock warnings
    def inventory_alert(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Low Stock ({} left)</span>', obj.stock_quantity)
        # THE FIX: We pass the text as an argument into the {} to satisfy Django's rules
        return format_html('<span style="color: green;">{}</span>', '✅ Healthy')
    inventory_alert.short_description = 'Stock Status'
    
    def image_tag(self, obj):
        if obj.image:
            # We restored your beautiful thumbnail logic!
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Image'
    
    class Media:
        css = {
            'all': ('store/admin_layout.css',)
        }

# 3. Order Management System
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # UPDATED: Added 'download_invoice' to the list_display array
    list_display = ('id', 'customer_display', 'total_amount', 'status', 'created_at', 'download_invoice')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)
    
    def customer_display(self, obj):
        return obj.customer.username if obj.customer else "Guest Customer"
    customer_display.short_description = 'Customer'

    class Media:
        css = {
            'all': ('store/admin_layout.css',) # <-- Updated path!
        }

    # NEW: Create a custom column that renders an HTML link to our PDF view
    def download_invoice(self, obj):
        url = reverse('dashboard:invoice_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}" style="background-color: #417690; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">📄 PDF</a>', url)
    download_invoice.short_description = 'Billing'

# 4. Billing & Invoice Tracker
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'issued_date', 'is_paid')
    list_filter = ('is_paid', 'issued_date')
    list_editable = ('is_paid',)

# 5. Register simple models
admin.site.register(Category)