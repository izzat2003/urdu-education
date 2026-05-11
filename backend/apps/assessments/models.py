"""
apps/assessments/models.py
Baholash tizimi: Topshiriqlar, Testlar, Baholar
Sillabus asosida: Amaliy + Mustaqil + Oraliq + Yakuniy
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# ══════════════════════════════════════════
# TOPSHIRIQLAR (ASSIGNMENTS)
# ══════════════════════════════════════════

class Assignment(models.Model):
    """
    O'qituvchi guruh uchun topshiriq yaratadi.
    Har bir topshiriq qaysi mavzuга va qaysi guruhga ekanligini ko'rsatadi.
    """
    
    class AssignmentType(models.TextChoices):
        AMALIY = 'amaliy', 'Amaliy mashg\'ulot'
        MUSTAQIL = 'mustaqil', 'Mustaqil ta\'lim'
        ORALIQ = 'oraliq', 'Oraliq nazorat'
    
    title = models.CharField(max_length=200, verbose_name='Topshiriq nomi')
    description = models.TextField(verbose_name='Topshiriq matni')
    
    topic = models.ForeignKey(
        'courses.Topic',
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Mavzu'
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='assignments',
        verbose_name='Guruh'
    )
    assignment_type = models.CharField(
        max_length=10,
        choices=AssignmentType.choices,
        default=AssignmentType.AMALIY,
        verbose_name='Tur'
    )
    deadline = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Muddati'
    )
    max_attempts = models.PositiveSmallIntegerField(
        default=3,
        verbose_name='Maksimal urinish soni'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_assignments',
        verbose_name='O\'qituvchi'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Topshiriq'
        verbose_name_plural = 'Topshiriqlar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.group.name} | {self.topic.code} | {self.title}"


class Submission(models.Model):
    """
    Talabaning topshiriq javobi.
    O'qituvchi baholaydi (2, 3, 4, 5).
    """
    
    class Grade(models.IntegerChoices):
        QONIQARSIZ = 2, 'Qoniqarsiz (2)'
        QONIQARLI  = 3, 'Qoniqarli (3)'
        YAXSHI     = 4, 'Yaxshi (4)'
        ALO        = 5, 'A\'lo (5)'
    
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Topshiriq'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name='Talaba'
    )
    
    # Javob
    text_answer = models.TextField(blank=True, verbose_name='Matn javobi')
    submitted_file = models.FileField(
        upload_to='submissions/',
        blank=True,
        null=True,
        verbose_name='Yuklangan fayl'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    attempt_number = models.PositiveSmallIntegerField(default=1)
    
    # Baholash
    grade = models.IntegerField(
        choices=Grade.choices,
        null=True,
        blank=True,
        verbose_name='Baho'
    )
    feedback = models.TextField(
        blank=True,
        verbose_name='O\'qituvchi izohi'
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions',
        verbose_name='Baholagan o\'qituvchi'
    )
    
    class Meta:
        verbose_name = 'Topshiriq javobi'
        verbose_name_plural = 'Topshiriq javoblari'
        ordering = ['-submitted_at']
    
    def __str__(self):
        grade_str = f" | Baho: {self.grade}" if self.grade else " | Baholanmagan"
        return f"{self.student.full_name} → {self.assignment.title}{grade_str}"


# ══════════════════════════════════════════
# TESTLAR
# ══════════════════════════════════════════

class Test(models.Model):
    """
    O'qituvchi guruh uchun test yaratadi.
    """
    title = models.CharField(max_length=200, verbose_name='Test nomi')
    topic = models.ForeignKey(
        'courses.Topic',
        on_delete=models.CASCADE,
        related_name='tests',
        verbose_name='Mavzu'
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        related_name='tests',
        verbose_name='Guruh'
    )
    time_limit_minutes = models.PositiveSmallIntegerField(
        default=30,
        verbose_name='Vaqt chegarasi (daqiqa)'
    )
    pass_score = models.PositiveSmallIntegerField(
        default=60,
        verbose_name='O\'tish bali (%)'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tests',
        verbose_name='O\'qituvchi'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Testlar'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.group.name} | {self.topic.code} | {self.title}"


class Question(models.Model):
    """Test savoli"""
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Test'
    )
    text = models.TextField(verbose_name='Savol matni')
    order = models.PositiveSmallIntegerField(default=1, verbose_name='Tartib')
    
    class Meta:
        verbose_name = 'Savol'
        verbose_name_plural = 'Savollar'
        ordering = ['order']
    
    def __str__(self):
        return f"#{self.order}: {self.text[:60]}"


class Choice(models.Model):
    """Savol uchun javob varianti"""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='Savol'
    )
    text = models.CharField(max_length=500, verbose_name='Javob matni')
    is_correct = models.BooleanField(default=False, verbose_name='To\'g\'ri javob')
    
    class Meta:
        verbose_name = 'Javob varianti'
        verbose_name_plural = 'Javob variantlari'
    
    def __str__(self):
        return f"{'✓' if self.is_correct else '✗'} {self.text[:40]}"


class TestAttempt(models.Model):
    """
    Talabaning test urinishi.
    Natija avtomatik hisoblanadi.
    """
    
    class Grade(models.IntegerChoices):
        QONIQARSIZ = 2, 'Qoniqarsiz (2)'
        QONIQARLI  = 3, 'Qoniqarli (3)'
        YAXSHI     = 4, 'Yaxshi (4)'
        ALO        = 5, 'A\'lo (5)'
    
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Test'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='test_attempts',
        verbose_name='Talaba'
    )
    
    score = models.FloatField(
        null=True, blank=True,
        verbose_name='Ball (%)'
    )  # 0.0 – 100.0
    
    grade = models.IntegerField(
        choices=Grade.choices,
        null=True, blank=True,
        verbose_name='Baho'
    )
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Test urinishi'
        verbose_name_plural = 'Test urinishlari'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.full_name} | {self.test.title} | {self.score}%"
    
    def calculate_grade(self):
        """Ball asosida 5-balli tizimda baho"""
        if self.score is None:
            return None
        if self.score >= 86:
            return 5
        elif self.score >= 71:
            return 4
        elif self.score >= 56:
            return 3
        else:
            return 2


class StudentAnswer(models.Model):
    """Talabaning har bir savolga javobi"""
    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Urinish'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='Savol'
    )
    chosen = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Tanlangan javob'
    )
    
    class Meta:
        unique_together = ['attempt', 'question']


# ══════════════════════════════════════════
# UMUMIY PROGRESS
# ══════════════════════════════════════════

class StudentProgress(models.Model):
    """
    Talabaning har bir mavzudagi yakuniy o'zlashtirishi.
    Sillabus mezonlari asosida: amaliy + mustaqil + oraliq + yakuniy
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progresses',
        verbose_name='Talaba'
    )
    topic = models.ForeignKey(
        'courses.Topic',
        on_delete=models.CASCADE,
        related_name='student_results',
        verbose_name='Mavzu'
    )
    
    # Baholar
    assignment_grade = models.IntegerField(null=True, blank=True)   # Amaliy
    test_grade = models.IntegerField(null=True, blank=True)          # Test
    overall_grade = models.IntegerField(null=True, blank=True)       # Umumiy
    
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Talaba o\'zlashtiruvi'
        verbose_name_plural = 'Talaba o\'zlashtirishlari'
        unique_together = ['student', 'topic']
        ordering = ['topic__order_number']
    
    def __str__(self):
        return f"{self.student.full_name} | {self.topic.code} | {self.overall_grade}"
    
    def compute_overall(self):
        """O'rtacha baho hisoblash"""
        grades = [g for g in [self.assignment_grade, self.test_grade] if g]
        if grades:
            self.overall_grade = round(sum(grades) / len(grades))
        return self.overall_grade
