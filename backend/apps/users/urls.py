"""apps/users/urls.py"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, MeView

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]
