"""SGCA - URLs principales"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Documentation API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API v1
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/academic/', include('apps.academic.urls')),
    path('api/v1/scheduling/', include('apps.scheduling.urls')),
    path('api/v1/prerequisites/', include('apps.prerequisites.urls')),
    path('api/v1/assignments/', include('apps.course_assignment.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
