from django.urls import path
from . import views

app_name = 'creator'

urlpatterns = [
    path('portal/', views.creator_portal, name='portal'),
    path('login/', views.custom_login, name='login'),
]