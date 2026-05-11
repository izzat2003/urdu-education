"""
apps/groups/models.py
Guruhlar modeli
Admin guruh yaratadi va talabalarni qo'shadi.
"""

from django.db import models
from django.conf import settings


class Group(models.Model):
    """
    O'quv guruhi.
    Admin yaratadi, o'qituvchi biriktiriladi.
    """
    name = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name='Guruh nomi'
    )  # Masalan: "22-DI-1", "23-KI-2"
    
    description = models.TextField(
        blank=True,
        verbose_name='Tavsif'
    )
    
    year = models.PositiveSmallIntegerField(
        verbose_name='O\'quv yili'
    )  # Masalan: 2025
    
    # O'qituvchi
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_groups',
        verbose_name='O\'qituvchi',
        limit_choices_to={'role': 'teacher'}
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Faol')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_groups',
        verbose_name='Yaratgan admin'
    )
    
    class Meta:
        verbose_name = 'Guruh'
        verbose_name_plural = 'Guruhlar'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def student_count(self):
        return self.students.filter(is_active=True).count()


class StudentGroup(models.Model):
    """
    Talaba ↔ Guruh aloqasi (Many-to-Many o'rniga explicit model)
    Bu orqali talabaning guruhga qo'shilgan sanasini kuzatish mumkin.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_groups',
        verbose_name='Talaba',
        limit_choices_to={'role': 'student'}
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='students',
        verbose_name='Guruh'
    )
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='Qo\'shilgan sana')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Guruh talabasi'
        verbose_name_plural = 'Guruh talabalari'
        unique_together = ['student', 'group']  # Bir talaba bir guruhda bir marta
        ordering = ['student__full_name']
    
    def __str__(self):
        return f"{self.student.full_name} → {self.group.name}"
