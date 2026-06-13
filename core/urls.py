
# core/urls.py
from django.contrib import admin
from django.urls import path, include

#urlpatterns = [
#    path('admin/', admin.site.urls),
#    path('dashboard/', include('dashboard.urls')),
#    path('', include('store.urls')),
#]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # B2C Storefront (Your original app)
    path('', include('store.urls')),
    
    # B2B Creator Portal (The new app)
    path('creator/', include('creator.urls', namespace='creator')),
]
# Rebrand the Django Admin Dashboard
from django.contrib import admin
admin.site.site_header = "Vibana Administration"
admin.site.site_title = "Vibana Admin Portal"
admin.site.index_title = "Welcome to the Vibana Store Manager"