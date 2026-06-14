import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from .models import Product, Category, Order, Invoice, Coupon, CustomerProfile, OrderItem
from .forms import CustomerRegistrationForm

def initiate_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_in_paise = int(order.total_amount * 100)
    
    data = {
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": f"receipt_order_{order.id}",
    }
    try:
        razorpay_order = client.order.create(data=data)
        order.razorpay_order_id = razorpay_order['id']
        order.save()
        
        context = {
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount_in_paise': amount_in_paise,
            'currency': 'INR',
            'callback_url': f"{request.scheme}://{request.get_host()}/store/payment/callback/",
        }
        return render(request, 'store/payment_checkout.html', context)
    except Exception as e:
        messages.error(request, f"Something went wrong: {str(e)}")
        return redirect('store:cart')
    
@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
            order = get_object_or_404(Order, razorpay_order_id=order_id)
            order.status = 'Processing'
            order.save()
            
            cart = request.session.get('cart', {})
            for product_id, quantity in cart.items():
                try:
                    product = Product.objects.get(id=int(product_id))
                    if product.stock_quantity >= quantity:
                        product.stock_quantity -= quantity
                        product.save()
                except Product.DoesNotExist:
                    continue
            
            if 'cart' in request.session:
                del request.session['cart']
                
            return render(request, 'store/payment_success.html', {'order': order, 'payment_id': payment_id})
            
        except razorpay.errors.SignatureVerificationError:
            return render(request, 'store/payment_failed.html')
            
    return HttpResponseBadRequest("Invalid request method.")

def catalog_view(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(name__icontains=search_query)

    category_id = request.GET.get('category')
    size = request.GET.get('size')
    color = request.GET.get('color')

    if category_id:
        products = products.filter(category_id=category_id)
    if size:
        products = products.filter(size=size)
    if color:
        products = products.filter(color__iexact=color)

    context = {
        'products': products,
        'categories': categories,
        'sizes': Product.SIZE_CHOICES if hasattr(Product, 'SIZE_CHOICES') else [],
        'current_filters': {
            'search': search_query,
            'category': category_id,
            'size': size,
            'color': color,
        }
    }
    return render(request, 'store/catalog.html', context)

def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    current_quantity = cart.get(str(product_id), 0)
    
    if current_quantity + 1 > product.stock_quantity:
        messages.error(request, f"Sorry, only {product.stock_quantity} units of this design are available.")
    else:
        cart[str(product_id)] = current_quantity + 1
        request.session['cart'] = cart
        messages.success(request, f"Added {product.name} to your cart.")
        
    return redirect('store:catalog')

def remove_from_cart_view(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.info(request, "Item removed from cart.")
    return redirect('store:cart_detail')

def cart_detail_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    grand_total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        total_price = product.price * quantity
        grand_total += total_price
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': total_price
        })

    discount_amount = 0
    coupon_id = request.session.get('coupon_id')
    coupon_code = None

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            coupon_code = coupon.code
            if coupon.discount_type == 'percentage':
                discount_amount = float(grand_total) * (float(coupon.discount_value) / 100)
            else:
                discount_amount = float(coupon.discount_value)
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None

    final_total = float(grand_total) - discount_amount
    if final_total < 0:
        final_total = 0

    context = {
        'cart_items': cart_items,
        'grand_total': grand_total,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'coupon_code': coupon_code
    }
    
    return render(request, 'store/cart.html', context)

def apply_coupon_view(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip()
        try:
            coupon = Coupon.objects.get(code__iexact=code)
            if coupon.is_valid():
                request.session['coupon_id'] = coupon.id
                messages.success(request, f"Promo code '{coupon.code}' applied successfully!")
            else:
                request.session['coupon_id'] = None
                messages.error(request, "This promo code is expired or has reached its usage limit.")
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
            messages.error(request, "Invalid promo code.")
            
    return redirect('store:cart_detail')

def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is completely empty.")
        return redirect('store:catalog')

    if request.method == 'POST':
        street = request.POST.get('street', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()

        if not all([street, pincode, city, state]):
            messages.error(request, "Please provide a complete and valid shipping address.")
            return redirect('store:checkout')

        address = f"{street}, {city}, {state} - {pincode}"

        receiver_name = request.POST.get('receiver_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        guest_email = None
        if not request.user.is_authenticated:
            guest_email = request.POST.get('guest_email', '').strip()
            
            if not all([guest_email, receiver_name, phone_number]):
                messages.error(request, "Guest checkout requires name, email, phone, and consent.")
                return redirect('store:cart')

        if not address:
            messages.error(request, "Please enter a valid shipping destination address.")
            return redirect('store:checkout')

        grand_total = 0
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=int(product_id))
            grand_total += product.price * quantity

        order = Order.objects.create(
            customer=request.user if request.user.is_authenticated else None,
            total_amount=grand_total,
            status='Pending',
            shipping_address=address,
            guest_email=guest_email,
            receiver_name=receiver_name,
            receiver_phone=phone_number
        )
        
        for product_id, quantity in cart.items():
            product = get_object_or_404(Product, id=int(product_id))
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=product.price
            )
            
        Invoice.objects.create(order=order, is_paid=False)

        return redirect('store:order_success', order_id=order.id)

    return render(request, 'store/checkout.html')

@login_required(login_url='/login/')
def customer_profile_view(request):
    profile, created = CustomerProfile.objects.get_or_create(user=request.user)
    user_orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    context = {
        'profile': profile,
        'orders': user_orders,
    }
    return render(request, 'store/profile.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('store:profile')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            CustomerProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f"Welcome to Vibana, {user.first_name}! Your account is ready.")
            return redirect('store:profile')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'store/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin:index')
        elif request.user.is_staff:
            return redirect('creator:portal')
        else:
            return redirect('store:profile')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Check role for correct redirect
                if user.is_superuser:
                    return redirect('admin:index')
                elif user.is_staff:
                    return redirect('creator:portal')
                else:
                    return redirect('store:profile')
    else:
        form = AuthenticationForm()

    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('store:catalog')

def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_success.html', {'order': order})

def convert_guest_view(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        password = request.POST.get('password')
        
        if order.customer is not None or not order.guest_email:
            return redirect('store:catalog')
            
        if User.objects.filter(email=order.guest_email).exists():
            messages.error(request, "An account with this email already exists. Please log in.")
            return redirect('store:login')

        user = User.objects.create_user(
            username=order.guest_email, 
            email=order.guest_email, 
            password=password
        )
        
        order.customer = user
        order.save()
        
        CustomerProfile.objects.get_or_create(user=user)
        login(request, user)
        
        messages.success(request, "Account created! Your order has been linked to your new dashboard.")
        return redirect('store:profile')
        
    return redirect('store:catalog')