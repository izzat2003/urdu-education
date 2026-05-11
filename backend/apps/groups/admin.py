"""apps/groups/admin.py"""
from django.contrib import admin
from .models import Group, StudentGroup


class StudentGroupInline(admin.TabularInline):
    model = StudentGroup
    extra = 0
    fields = ['student', 'joined_at', 'is_active']
    readonly_fields = ['joined_at']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'year', 'student_count', 'is_active']
    list_filter = ['is_active', 'year']
    search_fields = ['name']
    inlines = [StudentGroupInline]

    def student_count(self, obj):
        return obj.students.filter(is_active=True).count()
    student_count.short_description = 'Talabalar'
