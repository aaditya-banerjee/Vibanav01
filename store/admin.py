from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, CustomerProfile, Coupon

# 1. Product & Category Management
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_tag', 'category', 'size', 'color', 'price', 'stock_quantity', 'inventory_alert')
    list_filter = ('category', 'size', 'color')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock_quantity')

    def inventory_alert(self, obj):
        if obj.is_low_stock:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Low ({} left)</span>', obj.stock_quantity)
        return format_html('<span style="color: green;">✅ Healthy</span>')
    inventory_alert.short_description = 'Stock Status'

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Image'

admin.site.register(Category)

# 2. Customer & Marketing Tools
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'state')
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'active')
    list_filter = ('active', 'valid_from', 'valid_to', 'discount_type')
    search_fields = ('code',)