"""
apps/users/admin.py
Django admin panelida foydalanuvchilarni boshqarish
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'full_name', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'full_name', 'email']
    ordering = ['full_name']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Shaxsiy ma\'lumotlar', {'fields': ('full_name', 'email', 'phone')}),
        ('Rol va ruxsatlar', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Tizim', {'fields': ('created_by', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'full_name', 'role'),
        }),
    )
    readonly_fields = ['date_joined']
