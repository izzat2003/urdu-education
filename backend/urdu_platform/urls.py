"""
Urdu Education Platform — Asosiy URL konfiguratsiyasi
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Django admin (faqat superuser uchun)
    path('django-admin/', admin.site.urls),
    
    # JWT autentifikatsiya
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API endpointlar
    path('api/users/', include('apps.users.urls')),
    path('api/groups/', include('apps.groups.urls')),
    path('api/courses/', include('apps.courses.urls')),
    path('api/assessments/', include('apps.assessments.urls')),
]

# Development uchun media fayllar
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
