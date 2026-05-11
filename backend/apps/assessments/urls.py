"""apps/assessments/urls.py"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet, TestViewSet, StudentProgressViewSet

router = DefaultRouter()
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'tests', TestViewSet, basename='test')
router.register(r'progress', StudentProgressViewSet, basename='progress')

urlpatterns = [path('', include(router.urls))]
