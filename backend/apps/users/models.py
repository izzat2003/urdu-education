"""
apps/users/models.py
Foydalanuvchilar modeli — Admin, O'qituvchi, Talaba
MUHIM: Faqat Admin foydalanuvchi yarata oladi!
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    """Foydalanuvchi rollari"""
    ADMIN = 'admin', 'Admin'
    TEACHER = 'teacher', "O'qituvchi"
    STUDENT = 'student', 'Talaba'


class UserManager(BaseUserManager):
    """Maxsus foydalanuvchi menejeri"""
    
    def create_user(self, username, password, role, full_name, created_by=None, **extra_fields):
        """Oddiy foydalanuvchi yaratish"""
        if not username:
            raise ValueError("Login kiritilishi shart")
        if not password:
            raise ValueError("Parol kiritilishi shart")
        
        user = self.model(
            username=username,
            role=role,
            full_name=full_name,
            created_by=created_by,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password, **extra_fields):
        """Django superuser yaratish (faqat manage.py orqali)"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(
            username=username,
            password=password,
            role=UserRole.ADMIN,
            full_name=extra_fields.pop('full_name', 'Super Admin'),
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    """
    Platformaning asosiy foydalanuvchi modeli.
    Talaba va o'qituvchilar MUSTAQIL ro'yxatdan O'TA OLMAYDI.
    Ularni FAQAT Admin yaratadi.
    """
    
    # Asosiy maydonlar
    username = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='Login'
    )
    full_name = models.CharField(
        max_length=150, 
        verbose_name='To\'liq ismi'
    )
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        verbose_name='Rol'
    )
    
    # Qo'shimcha ma'lumotlar
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    
    # Tizim maydonlari
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    is_staff = models.BooleanField(default=False)  # Django admin uchun
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Ro\'yxatdan o\'tgan sana')
    
    # Kim yaratgan (Admin)
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name='Yaratgan admin'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    @property
    def is_teacher(self):
        return self.role == UserRole.TEACHER
    
    @property
    def is_student(self):
        return self.role == UserRole.STUDENT
