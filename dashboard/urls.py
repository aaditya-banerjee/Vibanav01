# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('invoice/<int:order_id>/pdf/', views.generate_invoice_pdf, name='invoice_pdf'),
]