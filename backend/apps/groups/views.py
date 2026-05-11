"""
apps/groups/views.py
Guruhlar uchun API view'lar
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Group, StudentGroup
from .serializers import GroupSerializer, GroupDetailSerializer, AddStudentSerializer
from apps.users.models import User, UserRole
from apps.users.permissions import IsAdmin, IsAdminOrTeacher


class GroupViewSet(viewsets.ModelViewSet):
    """
    Guruhlar CRUD operatsiyalari.
    
    GET    /api/groups/             — ro'yxat (Admin, O'qituvchi)
    POST   /api/groups/             — yaratish (Admin)
    GET    /api/groups/{id}/        — tafsilot (Admin, O'qituvchi)
    PATCH  /api/groups/{id}/        — tahrirlash (Admin)
    DELETE /api/groups/{id}/        — o'chirish (Admin)
    POST   /api/groups/{id}/add_students/    — talaba qo'shish (Admin)
    DELETE /api/groups/{id}/remove_student/ — talabani chiqarish (Admin)
    """
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy',
                           'add_students', 'remove_student']:
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsAdminOrTeacher()]
    
    def get_queryset(self):
        user = self.request.user
        
        # O'qituvchi faqat o'z guruhlarini ko'radi
        if user.is_teacher:
            return Group.objects.filter(teacher=user, is_active=True)
        
        # Admin hammasini ko'radi
        return Group.objects.all().order_by('name')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GroupDetailSerializer
        return GroupSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_students(self, request, pk=None):
        """
        Guruhga talabalar qo'shish.
        POST /api/groups/{id}/add_students/
        Body: {"student_ids": [1, 2, 3]}
        """
        group = self.get_object()
        serializer = AddStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        student_ids = serializer.validated_data['student_ids']
        students = User.objects.filter(id__in=student_ids, role=UserRole.STUDENT)
        
        added = []
        already_exists = []
        
        for student in students:
            sg, created = StudentGroup.objects.get_or_create(
                student=student,
                group=group,
                defaults={'is_active': True}
            )
            if created:
                added.append(student.full_name)
            else:
                if not sg.is_active:
                    sg.is_active = True
                    sg.save()
                    added.append(student.full_name)
                else:
                    already_exists.append(student.full_name)
        
        return Response({
            'message': f"{len(added)} ta talaba qo'shildi",
            'added': added,
            'already_in_group': already_exists
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'])
    def remove_student(self, request, pk=None):
        """
        Guruhdan talabani chiqarish.
        DELETE /api/groups/{id}/remove_student/?student_id=5
        """
        group = self.get_object()
        student_id = request.query_params.get('student_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id parametri kiritilishi shart'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            sg = StudentGroup.objects.get(group=group, student_id=student_id)
            sg.is_active = False
            sg.save()
            return Response({'message': 'Talaba guruhdan chiqarildi'})
        except StudentGroup.DoesNotExist:
            return Response(
                {'error': 'Talaba bu guruhda topilmadi'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Guruh statistikasi — O'qituvchi uchun.
        GET /api/groups/{id}/statistics/
        """
        from apps.assessments.models import StudentProgress
        
        group = self.get_object()
        students = group.students.filter(is_active=True).select_related('student')
        
        stats = []
        for sg in students:
            student = sg.student
            progress_list = StudentProgress.objects.filter(
                student=student
            ).select_related('topic')
            
            completed = progress_list.filter(is_completed=True).count()
            avg_grade = None
            grades = [p.overall_grade for p in progress_list if p.overall_grade]
            if grades:
                avg_grade = round(sum(grades) / len(grades), 1)
            
            stats.append({
                'student_id': student.id,
                'student_name': student.full_name,
                'username': student.username,
                'completed_topics': completed,
                'total_topics': 12,
                'average_grade': avg_grade,
                'progress_percent': round(completed / 12 * 100, 1)
            })
        
        return Response({
            'group': group.name,
            'teacher': group.teacher.full_name if group.teacher else None,
            'student_count': len(stats),
            'students': stats
        })
