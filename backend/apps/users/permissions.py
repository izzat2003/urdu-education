"""
apps/users/permissions.py
Rol asosidagi ruxsatlar (Role-Based Access Control)
"""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Faqat Admin uchun ruxsat"""
    message = "Bu amalni faqat Admin bajarishi mumkin"
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsTeacher(BasePermission):
    """Faqat O'qituvchi uchun ruxsat"""
    message = "Bu amalni faqat O'qituvchi bajarishi mumkin"
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_teacher)


class IsStudent(BasePermission):
    """Faqat Talaba uchun ruxsat"""
    message = "Bu amalni faqat Talaba bajarishi mumkin"
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_student)


class IsAdminOrTeacher(BasePermission):
    """Admin yoki O'qituvchi uchun ruxsat"""
    message = "Bu amalni faqat Admin yoki O'qituvchi bajarishi mumkin"
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.is_admin or request.user.is_teacher


class IsAdminOrTeacherOrReadOnly(BasePermission):
    """O'qish — hammaga, yozish — Admin yoki O'qituvchiga"""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.is_admin or request.user.is_teacher
