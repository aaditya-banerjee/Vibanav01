# Register your models here.

from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Order, Invoice, CustomerProfile, Coupon, DesignSubmission

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'state')
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'active')
    list_filter = ('active', 'valid_from', 'valid_to', 'discount_type')
    search_fields = ('code',)

@admin.register(DesignSubmission)
class DesignSubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'designer', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('title', 'designer__username')
    # Allows you to quickly approve/reject directly from the list view
    list_editable = ('status',)

@admin.register(DesignSubmission)
class DesignSubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'designer', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('title', 'designer__username')
    list_editable = ('status',) 

    # NEW: The Automation Engine
    def save_model(self, request, obj, form, change):
        # Check if the admin just marked this as 'approved', AND it hasn't been published yet
        if obj.status == 'approved' and not obj.final_product:
            
            # 1. Create a special category for community designs so it doesn't crash the database
            collab_category, created = Category.objects.get_or_create(
                name="Creator Collabs", 
                # If your Category model requires a slug or other fields, add them here!
                # slug="creator-collabs" 
            )

            # 2. Automatically build the live storefront product
            new_tshirt = Product.objects.create(
                name=obj.title,
                description=f"An exclusive design by {obj.designer.username}. {obj.description}",
                image=obj.image,
                category=collab_category,
                price=29.99,           # Default starting price
                stock_quantity=10,     # Give it initial stock so customers can buy it
                # Note: If your Product model strictly requires 'color' or 'size', add them here like: color='Black', size='M'
            )

            # 3. Link the live product back to the submission so the designer knows it was published
            obj.final_product = new_tshirt
            
        # Continue saving the model normally
        super().save_model(request, obj, form, change)