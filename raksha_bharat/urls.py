"""
URL routing for Raksha Bharat project.
Main URL configuration with API and web endpoints.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger/OpenAPI Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Raksha Bharat API",
        default_version='v1',
        description="Government Public Safety Platform API",
        terms_of_service="https://www.raksha-bharat.gov.in/terms/",
        contact=openapi.Contact(email="support@raksha-bharat.gov.in"),
        license=openapi.License(name="Government License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # API Documentation
    re_path(r'^api/docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^api/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Endpoints
    path('api/v1/auth/', include('core.urls')),
    path('api/v1/crime/', include('crime.urls')),
    path('api/v1/women-safety/', include('women_safety.urls')),
    path('api/v1/medical/', include('medical.urls')),
    path('api/v1/schemes/', include('schemes.urls')),
    path('api/v1/complaints/', include('complaints.urls')),
    path('api/v1/legal/', include('legal.urls')),
    path('api/v1/admin/', include('admin_panel.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    
    # Web Pages
    path('', include('core.web_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
