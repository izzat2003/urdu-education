"""
apps/assessments/views.py
Baholash tizimi: Topshiriqlar, Testlar, Baholar, Progress
"""

from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Avg, Count

from .models import (
    Assignment, Submission, Test, Question, Choice,
    TestAttempt, StudentAnswer, StudentProgress
)
from .serializers import (
    AssignmentSerializer, SubmissionSerializer,
    SubmissionCreateSerializer, GradeSubmissionSerializer,
    TestSerializer, TestDetailSerializer, TestStudentSerializer,
    TestAttemptSerializer, SubmitTestSerializer,
    StudentProgressSerializer, QuestionSerializer
)
from apps.users.permissions import IsAdmin, IsTeacher, IsStudent, IsAdminOrTeacher


# ══════════════════════════════════════════
# TOPSHIRIQLAR
# ══════════════════════════════════════════

class AssignmentViewSet(viewsets.ModelViewSet):
    """
    Topshiriqlar API.
    
    O'qituvchi: yaratish, ko'rish, tahrirlash (faqat o'z guruhlari uchun)
    Talaba: o'ziga tegishli topshiriqlarni ko'rish, topshirish
    """
    serializer_class = AssignmentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'grade_submission']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_teacher:
            # O'qituvchi faqat o'z guruhlarining topshiriqlarini ko'radi
            return Assignment.objects.filter(
                created_by=user
            ).select_related('topic', 'group').order_by('-created_at')
        
        if user.is_student:
            # Talaba o'z guruhlarining topshiriqlarini ko'radi
            from apps.groups.models import StudentGroup
            group_ids = StudentGroup.objects.filter(
                student=user, is_active=True
            ).values_list('group_id', flat=True)
            
            return Assignment.objects.filter(
                group_id__in=group_ids
            ).select_related('topic', 'group').order_by('deadline')
        
        # Admin — hammasi
        return Assignment.objects.all().select_related('topic', 'group')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """
        Topshiriqga kelgan barcha javoblar — O'qituvchi uchun.
        GET /api/assessments/assignments/{id}/submissions/
        """
        assignment = self.get_object()
        
        if not (request.user.is_teacher or request.user.is_admin):
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        subs = Submission.objects.filter(
            assignment=assignment
        ).select_related('student').order_by('-submitted_at')
        
        serializer = SubmissionSerializer(subs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Talaba topshiriq topshiradi.
        POST /api/assessments/assignments/{id}/submit/
        """
        assignment = self.get_object()
        
        if not request.user.is_student:
            return Response(
                {'error': 'Faqat talabalar topshiriq topshira oladi'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Deadline tekshiruvi
        if assignment.deadline and timezone.now() > assignment.deadline:
            return Response(
                {'error': 'Topshiriq muddati o\'tib ketgan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Urinish soni
        prev_attempts = Submission.objects.filter(
            assignment=assignment,
            student=request.user
        ).count()
        
        if prev_attempts >= assignment.max_attempts:
            return Response(
                {'error': f'Maksimal urinish soni ({assignment.max_attempts}) tugadi'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = SubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        sub = serializer.save(
            assignment=assignment,       # URL dan olingan assignment
            student=request.user,
            attempt_number=prev_attempts + 1
        )
        
        return Response(
            SubmissionSerializer(sub).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'], url_path='grade/(?P<submission_id>[^/.]+)')
    def grade_submission(self, request, submission_id=None, pk=None):
        """
        O'qituvchi topshiriqni baholaydi.
        POST /api/assessments/assignments/grade/{submission_id}/
        """
        try:
            sub = Submission.objects.get(id=submission_id)
        except Submission.DoesNotExist:
            return Response({'error': 'Topshiriq javobi topilmadi'}, status=404)
        
        serializer = GradeSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        sub.grade = serializer.validated_data['grade']
        sub.feedback = serializer.validated_data.get('feedback', '')
        sub.graded_at = timezone.now()
        sub.graded_by = request.user
        sub.save()
        
        # Progress yangilash
        _update_student_progress(sub.student, sub.assignment.topic)
        
        return Response({
            'message': 'Baho qo\'yildi',
            'grade': sub.grade,
            'feedback': sub.feedback
        })


# ══════════════════════════════════════════
# TESTLAR
# ══════════════════════════════════════════

class TestViewSet(viewsets.ModelViewSet):
    """Testlar API"""
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'add_questions']:
            return [IsAuthenticated(), IsAdminOrTeacher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_teacher:
            return Test.objects.filter(
                created_by=user
            ).select_related('topic', 'group')
        
        if user.is_student:
            from apps.groups.models import StudentGroup
            group_ids = StudentGroup.objects.filter(
                student=user, is_active=True
            ).values_list('group_id', flat=True)
            return Test.objects.filter(
                group_id__in=group_ids,
                is_active=True
            ).select_related('topic', 'group')
        
        return Test.objects.all()
    
    def get_serializer_class(self):
        user = self.request.user
        if self.action == 'retrieve':
            if user.is_student:
                return TestStudentSerializer
            return TestDetailSerializer
        return TestSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_questions(self, request, pk=None):
        """
        Testga savollar qo'shish.
        POST /api/assessments/tests/{id}/add_questions/
        Body: [{"text": "...", "order": 1, "choices": [{"text": "A", "is_correct": true}, ...]}]
        """
        test = self.get_object()
        questions_data = request.data
        
        if not isinstance(questions_data, list):
            return Response(
                {'error': 'Savollar ro\'yxat ko\'rinishida bo\'lishi kerak'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_questions = []
        for q_data in questions_data:
            serializer = QuestionSerializer(data={**q_data, 'test': test.id})
            serializer.is_valid(raise_exception=True)
            question = serializer.save()
            created_questions.append(question.id)
        
        return Response({
            'message': f"{len(created_questions)} ta savol qo'shildi",
            'question_ids': created_questions
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def start_attempt(self, request, pk=None):
        """
        Test urinishini boshlash.
        POST /api/assessments/tests/{id}/start_attempt/
        """
        test = self.get_object()
        
        if not request.user.is_student:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        # Mavjud tugallanmagan urinish bormi?
        existing = TestAttempt.objects.filter(
            test=test,
            student=request.user,
            completed_at__isnull=True
        ).first()
        
        if existing:
            return Response(
                TestAttemptSerializer(existing).data
            )
        
        attempt = TestAttempt.objects.create(
            test=test,
            student=request.user
        )
        
        return Response(
            TestAttemptSerializer(attempt).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def submit_attempt(self, request, pk=None):
        """
        Test javoblarini topshirish va avtomatik baholash.
        POST /api/assessments/tests/{id}/submit_attempt/
        Body: {"attempt_id": 1, "answers": [{"question_id": 1, "choice_id": 3}]}
        """
        test = self.get_object()
        
        attempt_id = request.data.get('attempt_id')
        answers_data = request.data.get('answers', [])
        
        try:
            attempt = TestAttempt.objects.get(
                id=attempt_id,
                test=test,
                student=request.user,
                completed_at__isnull=True
            )
        except TestAttempt.DoesNotExist:
            return Response(
                {'error': 'Faol urinish topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Javoblarni saqlash va hisoblash
        correct = 0
        total = 0
        
        for ans in answers_data:
            q_id = ans.get('question_id')
            c_id = ans.get('choice_id')
            
            try:
                question = Question.objects.get(id=q_id, test=test)
                choice = Choice.objects.get(id=c_id, question=question)
                
                StudentAnswer.objects.get_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={'chosen': choice}
                )
                
                total += 1
                if choice.is_correct:
                    correct += 1
            except (Question.DoesNotExist, Choice.DoesNotExist):
                continue
        
        # Ball va baho hisoblash
        score = round((correct / total * 100) if total > 0 else 0, 1)
        attempt.score = score
        attempt.grade = attempt.calculate_grade()
        attempt.completed_at = timezone.now()
        attempt.save()
        
        # Progress yangilash
        _update_student_progress(request.user, test.topic)
        
        return Response({
            'score': score,
            'grade': attempt.grade,
            'correct': correct,
            'total': total,
            'message': f"Test yakunlandi! Ball: {score}%, Baho: {attempt.grade}"
        })


# ══════════════════════════════════════════
# PROGRESS
# ══════════════════════════════════════════

class StudentProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Talaba o'zlashtiruvi.
    GET /api/assessments/progress/        — barcha mavzular
    GET /api/assessments/progress/{id}/   — bitta mavzu
    """
    serializer_class = StudentProgressSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_student:
            return StudentProgress.objects.filter(
                student=user
            ).select_related('topic').order_by('topic__order_number')
        
        # O'qituvchi / Admin — so'rovda student_id bo'lsa
        student_id = self.request.query_params.get('student_id')
        if student_id:
            return StudentProgress.objects.filter(
                student_id=student_id
            ).select_related('topic')
        
        return StudentProgress.objects.none()
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Talabaning umumiy o'zlashtiruv xulasasi.
        GET /api/assessments/progress/summary/
        """
        progresses = self.get_queryset()
        
        grades = [p.overall_grade for p in progresses if p.overall_grade]
        avg = round(sum(grades) / len(grades), 2) if grades else 0
        
        return Response({
            'total_topics': 12,
            'completed': progresses.filter(is_completed=True).count(),
            'average_grade': avg,
            'grades_breakdown': {
                '5': len([g for g in grades if g == 5]),
                '4': len([g for g in grades if g == 4]),
                '3': len([g for g in grades if g == 3]),
                '2': len([g for g in grades if g == 2]),
            }
        })


# ══════════════════════════════════════════
# YORDAMCHI FUNKSIYALAR
# ══════════════════════════════════════════

def _update_student_progress(student, topic):
    """
    Talabaning mavzudagi o'zlashtirishini yangilash.
    Topshiriq baholanganda yoki test yakunlanganda chaqiriladi.
    """
    from apps.courses.models import TopicProgress
    from apps.courses.views import unlock_next_topic
    
    progress, _ = StudentProgress.objects.get_or_create(
        student=student,
        topic=topic
    )
    
    # Eng so'ngi topshiriq bahasini olish
    last_sub = Submission.objects.filter(
        student=student,
        assignment__topic=topic,
        grade__isnull=False
    ).order_by('-graded_at').first()
    
    if last_sub:
        progress.assignment_grade = last_sub.grade
    
    # Test bahasini olish
    last_attempt = TestAttempt.objects.filter(
        student=student,
        test__topic=topic,
        completed_at__isnull=False
    ).order_by('-completed_at').first()
    
    if last_attempt:
        progress.test_grade = last_attempt.grade
    
    # O'rtacha hisoblash
    progress.compute_overall()
    
    # Mavzu yakunlangan?
    tp = TopicProgress.objects.filter(student=student, topic=topic).first()
    
    if (progress.assignment_grade and 
        progress.test_grade and 
        tp and tp.lesson_viewed):
        
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        
        # TopicProgress yangilash
        if tp.status != 'completed':
            tp.status = 'completed'
            tp.completed_at = timezone.now()
            tp.save()
        
        # Keyingi mavzuni ochish
        unlock_next_topic(student, topic)
    else:
        progress.save()
