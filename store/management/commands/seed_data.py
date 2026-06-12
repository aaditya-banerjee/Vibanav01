from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from store.models import Category, Product

class Command(BaseCommand):
    help = 'Seeds security role groups and initial T-shirt catalog inventory'

    def handle(self, *args, **kwargs):
        # 1. Initialize Role Groups
        staff_group, _ = Group.objects.get_or_create(name='Staff')
        customer_group, _ = Group.objects.get_or_create(name='Customer')

        # 2. Extract Product Content Target permissions
        product_content_type = ContentType.objects.get_for_model(Product)
        
        # Staff members can view, add, and update inventory, but cannot delete products
        staff_permissions = Permission.objects.filter(
            content_type=product_content_type,
            codename__in=['add_product', 'change_product', 'view_product']
        )
        staff_group.permissions.set(staff_permissions)

        # 3. Seed Product Categories
        graphic_tees, _ = Category.objects.get_or_create(name='Graphic Tees')
        plain_basics, _ = Category.objects.get_or_create(name='Plain Basics')

        # 4. Seed Core Inventory Items
        Product.objects.get_or_create(
            name='Vintage Rock Graphic Tee',
            category=graphic_tees,
            description='A retro style black cotton T-shirt featuring a vintage band layout.',
            price=29.99,
            size='M',
            color='Black',
            stock_quantity=50,
            low_stock_threshold=10
        )
        
        # This second product is seeded below its threshold to verify low-stock alert highlights later
        Product.objects.get_or_create(
            name='Classic Organic White Crewneck',
            category=plain_basics,
            description='Premium light, sustainable organic cotton basic everyday tee.',
            price=19.99,
            size='L',
            color='White',
            stock_quantity=4, 
            low_stock_threshold=10
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with security roles and inventory items!'))