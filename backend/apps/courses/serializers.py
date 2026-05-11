"""
apps/courses/serializers.py
"""

from rest_framework import serializers
from .models import Topic, TopicProgress


class TopicListSerializer(serializers.ModelSerializer):
    """Mavzular ro'yxati uchun (qisqa)"""
    
    class Meta:
        model = Topic
        fields = [
            'id', 'code', 'title', 'order_number',
            'is_published', 'lecture_duration',
            'video_url', 'visualization_type'
        ]


class TopicDetailSerializer(serializers.ModelSerializer):
    """Mavzu tafsilotlari (to'liq)"""
    
    class Meta:
        model = Topic
        fields = [
            'id', 'code', 'title', 'description', 'order_number',
            'lecture_content', 'pseudo_code', 'real_code', 'code_language',
            'visualization_type', 'video_url', 'pdf_file',
            'is_published', 'lecture_duration',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TopicCreateSerializer(serializers.ModelSerializer):
    """Mavzu yaratish/tahrirlash (O'qituvchi)"""
    
    class Meta:
        model = Topic
        fields = [
            'code', 'title', 'description',
            'lecture_content', 'pseudo_code', 'real_code', 'code_language',
            'visualization_type', 'video_url', 'pdf_file',
            'is_published', 'lecture_duration'
        ]
    
    def validate_code(self, value):
        """Har bir kod faqat bir marta bo'lishi mumkin (update uchun ruxsat)"""
        instance = self.instance
        if Topic.objects.filter(code=value).exclude(
            pk=instance.pk if instance else None
        ).exists():
            raise serializers.ValidationError(
                f"{value} kodi allaqachon mavjud"
            )
        return value


class TopicProgressSerializer(serializers.ModelSerializer):
    """Talabaning mavzu holati"""
    topic_code = serializers.CharField(source='topic.code', read_only=True)
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    topic_order = serializers.IntegerField(source='topic.order_number', read_only=True)
    
    class Meta:
        model = TopicProgress
        fields = [
            'id', 'topic', 'topic_code', 'topic_title', 'topic_order',
            'status', 'lesson_viewed', 'lesson_viewed_at',
            'unlocked_at', 'completed_at'
        ]
        read_only_fields = ['id', 'unlocked_at', 'completed_at']


class StudentTopicStatusSerializer(serializers.ModelSerializer):
    """
    Talabaga mavzu ro'yxatini progress bilan qaytarish.
    Har bir mavzu uchun: holat, baho, ochiqmi.
    """
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = [
            'id', 'code', 'title', 'order_number',
            'is_published', 'video_url', 'visualization_type',
            'progress'
        ]
    
    def get_progress(self, topic):
        student = self.context.get('student')
        if not student:
            return None
        
        try:
            tp = TopicProgress.objects.get(student=student, topic=topic)
            return {
                'status': tp.status,
                'lesson_viewed': tp.lesson_viewed,
                'unlocked_at': tp.unlocked_at,
                'completed_at': tp.completed_at,
            }
        except TopicProgress.DoesNotExist:
            return {
                'status': 'locked',
                'lesson_viewed': False,
                'unlocked_at': None,
                'completed_at': None,
            }
