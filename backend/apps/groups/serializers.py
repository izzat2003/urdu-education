"""
apps/groups/serializers.py
"""

from rest_framework import serializers
from .models import Group, StudentGroup
from apps.users.serializers import UserListSerializer


class GroupSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'year', 'teacher', 'teacher_name',
                  'is_active', 'student_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'student_count']


class GroupDetailSerializer(GroupSerializer):
    """Guruh tafsilotlari (talabalar ro'yxati bilan)"""
    students_list = serializers.SerializerMethodField()
    
    class Meta(GroupSerializer.Meta):
        fields = GroupSerializer.Meta.fields + ['students_list']
    
    def get_students_list(self, obj):
        student_groups = obj.students.filter(is_active=True).select_related('student')
        return [
            {
                'id': sg.student.id,
                'full_name': sg.student.full_name,
                'username': sg.student.username,
                'joined_at': sg.joined_at
            }
            for sg in student_groups
        ]


class AddStudentSerializer(serializers.Serializer):
    """Guruhga talaba qo'shish"""
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
