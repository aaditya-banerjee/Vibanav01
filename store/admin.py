# Register your models here.

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, CustomerProfile  # Add CustomerProfile here

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'state')
    search_fields = ('user__username', 'user__email', 'phone_number')