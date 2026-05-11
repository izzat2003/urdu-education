"""apps/courses/admin.py"""
from django.contrib import admin
from .models import Topic, TopicProgress


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'order_number', 'is_published', 'code_language', 'visualization_type']
    list_filter = ['is_published', 'code_language', 'visualization_type']
    search_fields = ['code', 'title']
    ordering = ['order_number']
    list_editable = ['is_published']


@admin.register(TopicProgress)
class TopicProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'topic', 'status', 'lesson_viewed', 'completed_at']
    list_filter = ['status', 'lesson_viewed']
    search_fields = ['student__full_name', 'topic__code']
    ordering = ['student__full_name', 'topic__order_number']
