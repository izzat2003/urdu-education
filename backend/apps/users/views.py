"""
apps/users/views.py
Foydalanuvchilar uchun API view'lar
"""

from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import User, UserRole
from .serializers import (
    UserCreateSerializer, UserListSerializer, 
    UserUpdateSerializer, MeSerializer
)
from .permissions import IsAdmin, IsAdminOrTeacher


class MeView(generics.RetrieveAPIView):
    """Joriy foydalanuvchi ma'lumotlarini olish — /api/users/me/"""
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """
    Foydalanuvchilar CRUD operatsiyalari.
    
    GET    /api/users/         — ro'yxat (Admin)
    POST   /api/users/         — yaratish (Admin)
    GET    /api/users/{id}/    — ko'rish (Admin)
    PATCH  /api/users/{id}/    — tahrirlash (Admin)
    DELETE /api/users/{id}/    — o'chirish (Admin)
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'full_name', 'email']
    
    def get_queryset(self):
        return User.objects.exclude(
            id=self.request.user.id  # O'zini ko'rsatmasin
        ).order_by('role', 'full_name')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserListSerializer
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def students(self, request):
        """Faqat talabalar ro'yxati — /api/users/students/"""
        qs = User.objects.filter(role=UserRole.STUDENT, is_active=True)
        serializer = UserListSerializer(qs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def teachers(self, request):
        """Faqat o'qituvchilar ro'yxati — /api/users/teachers/"""
        qs = User.objects.filter(role=UserRole.TEACHER, is_active=True)
        serializer = UserListSerializer(qs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Umumiy statistika — /api/users/stats/"""
        return Response({
            'total_users': User.objects.count(),
            'total_students': User.objects.filter(role=UserRole.STUDENT).count(),
            'total_teachers': User.objects.filter(role=UserRole.TEACHER).count(),
            'active_students': User.objects.filter(role=UserRole.STUDENT, is_active=True).count(),
        })
