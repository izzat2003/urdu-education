"""
apps/assessments/serializers.py
"""

from rest_framework import serializers
from .models import (
    Assignment, Submission,
    Test, Question, Choice, TestAttempt, StudentAnswer,
    StudentProgress
)


# ── Topshiriqlar ──────────────────────────────────────

class AssignmentSerializer(serializers.ModelSerializer):
    topic_code = serializers.CharField(source='topic.code', read_only=True)
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    submission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'topic', 'topic_code', 'topic_title',
            'group', 'group_name', 'assignment_type', 'deadline',
            'max_attempts', 'submission_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_submission_count(self, obj):
        return obj.submissions.count()


class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'assignment_title',
            'student', 'student_name',
            'text_answer', 'submitted_file', 'submitted_at', 'attempt_number',
            'grade', 'feedback', 'graded_at'
        ]
        read_only_fields = ['id', 'submitted_at', 'grade', 'feedback', 'graded_at', 'graded_by']


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Talaba topshiriq topshirish uchun"""
    
    class Meta:
        model = Submission
        fields = ['text_answer', 'submitted_file']
        extra_kwargs = {
            'text_answer': {'required': False, 'allow_blank': True},
            'submitted_file': {'required': False},
        }
    
    def validate(self, attrs):
        """Matn yoki fayl — bittasi bo'lishi shart"""
        text = attrs.get('text_answer', '').strip()
        file = attrs.get('submitted_file')
        if not text and not file:
            raise serializers.ValidationError(
                'Matn javob yoki fayl yuklash — kamida bittasi bo\'lishi kerak'
            )
        return attrs


class GradeSubmissionSerializer(serializers.Serializer):
    """O'qituvchi baholash uchun"""
    grade = serializers.ChoiceField(choices=[2, 3, 4, 5])
    feedback = serializers.CharField(required=False, allow_blank=True)


# ── Testlar ────────────────────────────────────────────

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct']


class ChoiceStudentSerializer(serializers.ModelSerializer):
    """Talabaga is_correct ko'rsatilmaydi"""
    class Meta:
        model = Choice
        fields = ['id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'choices']
    
    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        question = Question.objects.create(**validated_data)
        for c in choices_data:
            Choice.objects.create(question=question, **c)
        return question


class QuestionStudentSerializer(serializers.ModelSerializer):
    """Talabaga to'g'ri javob ko'rsatilmaydi"""
    choices = ChoiceStudentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'order', 'choices']


class TestSerializer(serializers.ModelSerializer):
    topic_code = serializers.CharField(source='topic.code', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Test
        fields = [
            'id', 'title', 'topic', 'topic_code', 'group', 'group_name',
            'time_limit_minutes', 'pass_score', 'question_count',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_question_count(self, obj):
        return obj.questions.count()


class TestDetailSerializer(TestSerializer):
    """O'qituvchi uchun — to'g'ri javoblar ko'rinadi"""
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta(TestSerializer.Meta):
        fields = TestSerializer.Meta.fields + ['questions']


class TestStudentSerializer(TestSerializer):
    """Talaba uchun — to'g'ri javoblar ko'rinmaydi"""
    questions = QuestionStudentSerializer(many=True, read_only=True)
    
    class Meta(TestSerializer.Meta):
        fields = TestSerializer.Meta.fields + ['questions']


class TestAttemptSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)
    
    class Meta:
        model = TestAttempt
        fields = [
            'id', 'test', 'test_title', 'student',
            'score', 'grade', 'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'score', 'grade', 'started_at', 'completed_at']


class SubmitTestSerializer(serializers.Serializer):
    """Test javoblarini topshirish"""
    answers = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField())
    )
    # Format: [{"question_id": 1, "choice_id": 3}, ...]


# ── Progress ────────────────────────────────────────────

class StudentProgressSerializer(serializers.ModelSerializer):
    topic_code = serializers.CharField(source='topic.code', read_only=True)
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    
    class Meta:
        model = StudentProgress
        fields = [
            'id', 'topic', 'topic_code', 'topic_title',
            'assignment_grade', 'test_grade', 'overall_grade',
            'is_completed', 'completed_at'
        ]
