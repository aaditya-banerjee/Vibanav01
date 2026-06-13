# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', '1X Large'),
        ('XXL', '2X Large'),
        ('XXXL', '3X Large')
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    stock_quantity = models.PositiveIntegerField(default=0)
    stock = models.IntegerField(default=0, help_text="Current available inventory")
    low_stock_threshold = models.PositiveIntegerField(default=10)
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.name} ({self.size} / {self.color})"

    def is_in_stock(self):
        """Quick check to see if we can sell this item."""
        return self.stock > 0

    def deduct_stock(self, quantity=1):
        """Safely deducts stock only if available."""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled')
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='orders')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        customer_name = self.customer.username if self.customer else "Guest Customer"
        return f"Order #{self.id} - {customer_name}"

class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    issued_date = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice #{self.id} for Order #{self.order.id}"

class CustomerProfile(models.Model):
    # The OneToOneField strictly links this profile to Django's native authentication
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Shipping & Contact Info
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Payment Gateway Link (For future saved-card features)
    razorpay_customer_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text="e.g., SUMMER20")
    
    DISCOUNT_TYPES = (
        ('percentage', 'Percentage (%)'),
        ('flat', 'Flat Amount (₹)'), # Updated to INR for Vibana
    )
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Enter 20 for 20%, or 100.00 for ₹100 off")
    
    # Time Constraints
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    
    # Usage Constraints
    active = models.BooleanField(default=True)
    max_uses = models.IntegerField(default=100)
    current_uses = models.IntegerField(default=0)
    
    def is_valid(self):
        """The brain of the promo code."""
        now = timezone.now()
        if not self.active:
            return False
        if self.current_uses >= self.max_uses:
            return False
        if now < self.valid_from or now > self.valid_to:
            return False
        return True

    def __str__(self):
        return self.code

class DesignSubmission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved & Listed'),
        ('rejected', 'Needs Revisions'),
    )

    designer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='submissions/images/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_feedback = models.TextField(blank=True, help_text="Notes for the designer if rejected.")
    submitted_at = models.DateTimeField(auto_now_add=True)
    final_product = models.OneToOneField('Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='original_submission')

    def __str__(self):
        return f'"{self.title}" by {self.designer.username} - {self.get_status_display()}'

class OrderItem(models.Model):
    """Tracks individual products within a specific order."""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Order #{self.order.id})"