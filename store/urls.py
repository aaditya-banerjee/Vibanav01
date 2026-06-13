# store/urls.py
from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/initiate/<int:order_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    # Legal & Compliance Pages
    path('terms/', TemplateView.as_view(template_name="store/terms.html"), name='terms'),
    path('privacy/', TemplateView.as_view(template_name="store/privacy.html"), name='privacy'),
    path('refunds/', TemplateView.as_view(template_name="store/refunds.html"), name='refunds'),
    # Coupons
    path('apply-coupon/', views.apply_coupon_view, name='apply_coupon'),
    path('creator-portal/', views.creator_portal, name='creator_portal'),
]