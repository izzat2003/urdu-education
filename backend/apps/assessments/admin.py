"""apps/assessments/admin.py"""
from django.contrib import admin
from .models import (
    Assignment, Submission,
    Test, Question, Choice, TestAttempt, StudentAnswer,
    StudentProgress
)


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    fields = ['student', 'grade', 'submitted_at']
    readonly_fields = ['submitted_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'topic', 'assignment_type', 'deadline', 'created_by']
    list_filter = ['assignment_type', 'group']
    search_fields = ['title', 'group__name']
    inlines = [SubmissionInline]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'grade', 'submitted_at', 'graded_by']
    list_filter = ['grade']
    search_fields = ['student__full_name', 'assignment__title']


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'topic', 'time_limit_minutes', 'is_active']
    list_filter = ['is_active', 'group']
    search_fields = ['title']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'test', 'order']
    inlines = [ChoiceInline]


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'test', 'score', 'grade', 'completed_at']
    list_filter = ['grade']
    search_fields = ['student__full_name']


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'topic', 'assignment_grade', 'test_grade', 'overall_grade', 'is_completed']
    list_filter = ['is_completed', 'overall_grade']
    search_fields = ['student__full_name', 'topic__code']
    ordering = ['student__full_name', 'topic__order_number']
