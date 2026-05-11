"""
apps/courses/views.py
Kurs mavzulari uchun API view'lar
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Topic, TopicProgress
from .serializers import (
    TopicListSerializer, TopicDetailSerializer,
    TopicCreateSerializer, TopicProgressSerializer,
    StudentTopicStatusSerializer
)
from apps.users.permissions import IsAdmin, IsTeacher, IsAdminOrTeacher


class TopicViewSet(viewsets.ModelViewSet):
    """
    Mavzular API.
    
    O'qituvchi: yaratish, tahrirlash
    Talaba: ko'rish (faqat ochilgan mavzular)
    Admin: hammasi
    """
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        qs = Topic.objects.all().order_by('order_number')
        
        # Talaba faqat nashr qilingan mavzularni ko'radi
        if user.is_student:
            return qs.filter(is_published=True)
        
        return qs
    
    def get_serializer_class(self):
        user = self.request.user
        
        if self.action in ['create', 'update', 'partial_update']:
            return TopicCreateSerializer
        
        if self.action == 'list':
            if user.is_student:
                return StudentTopicStatusSerializer
            return TopicListSerializer
        
        return TopicDetailSerializer
    
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.request.user.is_student:
            ctx['student'] = self.request.user
        return ctx
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        topic = self.get_object()
        
        # Talaba uchun: mavzu ochiqmi?
        if request.user.is_student:
            tp = TopicProgress.objects.filter(
                student=request.user,
                topic=topic
            ).first()
            
            if not tp or tp.status == 'locked':
                return Response(
                    {'error': 'Bu mavzu hali ochilmagan. Oldingi mavzuni yakunlang.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(topic)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_lesson_viewed(self, request, pk=None):
        """
        Talaba darsni ko'rdi deb belgilash.
        POST /api/courses/{id}/mark_lesson_viewed/
        """
        topic = self.get_object()
        user = request.user
        
        if not user.is_student:
            return Response(
                {'error': 'Faqat talabalar uchun'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tp, created = TopicProgress.objects.get_or_create(
            student=user,
            topic=topic
        )
        
        if tp.status == 'locked':
            return Response(
                {'error': 'Bu mavzu qulflangan'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not tp.lesson_viewed:
            tp.lesson_viewed = True
            tp.lesson_viewed_at = timezone.now()
            if tp.status == 'unlocked':
                tp.status = 'in_progress'
            tp.save()
        
        return Response({
            'message': 'Dars ko\'rildi deb belgilandi',
            'lesson_viewed': tp.lesson_viewed
        })
    
    @action(detail=False, methods=['get'])
    def my_progress(self, request):
        """
        Talabaning barcha mavzulardagi holati.
        GET /api/courses/my_progress/
        """
        if not request.user.is_student:
            return Response(
                {'error': 'Faqat talabalar uchun'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        progresses = TopicProgress.objects.filter(student=request.user)
        if not progresses.exists():
            _initialize_progress(request.user)
            progresses = TopicProgress.objects.filter(student=request.user)
            
        topics = Topic.objects.filter(is_published=True).order_by('order_number')
        serializer = StudentTopicStatusSerializer(
            topics,
            many=True,
            context={'student': request.user, 'request': request}
        )
        
        # Umumiy statistika
        completed_count = progresses.filter(status='completed').count()
        total_topics = topics.count()
        progress_percent = round(completed_count / total_topics * 100, 1) if total_topics > 0 else 0
        
        return Response({
            'completed_topics': completed_count,
            'total_topics': total_topics,
            'progress_percent': progress_percent,
            'topics': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def initialize_student_progress(self, request):
        """
        Yangi talaba uchun progress boshlash (M1 ochiladi).
        Admin tomonidan talaba yaratilganda chaqiriladi.
        POST /api/courses/initialize_student_progress/
        Body: {"student_id": 5}
        """
        if not request.user.is_admin:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        from apps.users.models import User
        student_id = request.data.get('student_id')
        
        try:
            student = User.objects.get(id=student_id, role='student')
        except User.DoesNotExist:
            return Response({'error': 'Talaba topilmadi'}, status=404)
        
        _initialize_progress(student)
        
        return Response({'message': f"{student.full_name} uchun progress boshlandi"})


def _initialize_progress(student):
    """
    Talaba uchun barcha mavzular progress yozuvini yaratish.
    Faqat M1 'unlocked', qolganlari 'locked'.
    """
    topics = Topic.objects.filter(is_published=True).order_by('order_number')
    
    for i, topic in enumerate(topics):
        tp, created = TopicProgress.objects.get_or_create(
            student=student,
            topic=topic,
            defaults={
                'status': 'unlocked' if i == 0 else 'locked',
                'unlocked_at': timezone.now() if i == 0 else None
            }
        )
    
    return True


def unlock_next_topic(student, completed_topic):
    """
    Mavzu yakunlanganda keyingisini ochish.
    Bu funksiya assessments signal/view'dan chaqiriladi.
    """
    next_topic = Topic.objects.filter(
        order_number=completed_topic.order_number + 1,
        is_published=True
    ).first()
    
    if next_topic:
        tp, _ = TopicProgress.objects.get_or_create(
            student=student,
            topic=next_topic
        )
        if tp.status == 'locked':
            tp.status = 'unlocked'
            tp.unlocked_at = timezone.now()
            tp.save()
        return next_topic
    
    return None  # Oxirgi mavzu
