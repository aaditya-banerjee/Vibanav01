# Register your models here.

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, CustomerProfile  # Add CustomerProfile here
from .models import Product, Category, Order, Invoice, CustomerProfile, Coupon


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'state')
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'active')
    list_filter = ('active', 'valid_from', 'valid_to', 'discount_type')
    search_fields = ('code',)