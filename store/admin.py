# Register your models here.

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Order, Invoice, CustomerProfile, Coupon, DesignSubmission

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'state')
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(DesignSubmission)
class DesignSubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'designer', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('title', 'designer__username')
    # Allows you to quickly approve/reject directly from the list view
    list_editable = ('status',)