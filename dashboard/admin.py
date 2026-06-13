from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from store.models import Order, Invoice, DesignSubmission, Category, Product

# 1. Global Dashboard Branding
admin.site.site_header = "Vibana HQ Administration"
admin.site.site_title = "Vibana Admin Portal"
admin.site.index_title = "Welcome to Mission Control"

# 2. Order Management System
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_display', 'total_amount', 'status', 'created_at', 'download_invoice')
    list_filter = ('status', 'created_at')
    list_editable = ('status',)

    def customer_display(self, obj):
        return obj.customer.username if obj.customer else "Guest Customer"
    customer_display.short_description = 'Customer'

    # Notice the perfectly mapped namespace: 'dashboard:invoice_pdf'
    def download_invoice(self, obj):
        url = reverse('dashboard:invoice_pdf', args=[obj.id])
        return format_html('<a class="button" href="{}" style="background-color: #ffc107; color: #1a1d20; padding: 4px 10px; border-radius: 4px; text-decoration: none; font-weight: bold;">📄 PDF</a>', url)
    download_invoice.short_description = 'Billing'

# 3. Billing & Invoice Tracker
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'issued_date', 'is_paid')
    list_filter = ('is_paid', 'issued_date')
    list_editable = ('is_paid',)

# 4. Creator Workflow Automation Engine
@admin.register(DesignSubmission)
class DesignSubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'designer', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('title', 'designer__username')
    list_editable = ('status',)

    def save_model(self, request, obj, form, change):
        if obj.status == 'approved' and not obj.final_product:
            collab_category, created = Category.objects.get_or_create(name="Creator Collabs")
            new_tshirt = Product.objects.create(
                name=obj.title,
                description=f"An exclusive design by {obj.designer.username}. {obj.description}",
                image=obj.image,
                category=collab_category,
                price=29.99,
                stock_quantity=10,
            )
            obj.final_product = new_tshirt
        super().save_model(request, obj, form, change)