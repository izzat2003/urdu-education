"""
apps/users/serializers.py
Foydalanuvchilar uchun serializerlar
"""

from rest_framework import serializers
from .models import User, UserRole


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Foydalanuvchi yaratish uchun serializer.
    FAQAT Admin ishlatadi.
    """
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'full_name', 'role', 'email', 'phone']
        read_only_fields = ['id']
    
    def validate_role(self, value):
        """Admin o'zini admin qila olmasligi uchun"""
        request = self.context.get('request')
        if request and not request.user.is_admin:
            raise serializers.ValidationError("Faqat admin foydalanuvchi yarata oladi")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        request = self.context.get('request')
        
        user = User(**validated_data)
        user.set_password(password)
        user.created_by = request.user if request else None
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    """Foydalanuvchilar ro'yxati uchun"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'role_display', 
                  'email', 'phone', 'is_active', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Foydalanuvchini tahrirlash (parolsiz)"""
    new_password = serializers.CharField(write_only=True, required=False, min_length=6)
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'is_active', 'new_password']
    
    def update(self, instance, validated_data):
        new_password = validated_data.pop('new_password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if new_password:
            instance.set_password(new_password)
        
        instance.save()
        return instance


class MeSerializer(serializers.ModelSerializer):
    """Joriy foydalanuvchi ma'lumotlari"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'role_display', 'email', 'phone']
