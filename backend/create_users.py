import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'urdu_platform.settings')
django.setup()

from apps.users.models import User

# Ensure admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin123', full_name='Tizim Administratori')
else:
    u = User.objects.get(username='admin')
    u.set_password('admin123')
    u.save()

# Ensure teacher
if not User.objects.filter(username='teacher').exists():
    User.objects.create_user('teacher', 'teacher123', 'teacher', 'Uktamjon Madaminov')
else:
    u = User.objects.get(username='teacher')
    u.set_password('teacher123')
    u.save()

# Ensure student
if not User.objects.filter(username='student').exists():
    User.objects.create_user('student', 'student123', 'student', 'Test Talaba')
else:
    u = User.objects.get(username='student')
    u.set_password('student123')
    u.save()

print("Users created/updated successfully.")
