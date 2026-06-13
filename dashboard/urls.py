# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # We will map your invoice view here
    path('invoice/<int:order_id>/', views.invoice_pdf, name='invoice_pdf'),
]
