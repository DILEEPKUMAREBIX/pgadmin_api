"""
URL configuration for pgadmin_config project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from properties.views_health import health_check, ready_check

urlpatterns = [
    # Health checks for Cloud Run
    path('health/', health_check, name='health'),
    path('ready/', ready_check, name='ready'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API
    path('api/', include('properties.urls')),
    path('api/v1/', include('properties.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
]

