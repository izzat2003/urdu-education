"""
apps/courses/models.py
Kurs mavzulari (M1-M12) — Sillabus asosida
"""

from django.db import models
from django.conf import settings


class TopicCode(models.TextChoices):
    """MTA kursining 12 ta asosiy mavzusi"""
    M1  = 'M1',  'M1: Abstrakt tuzilmalar. Algoritmlar tahlili'
    M2  = 'M2',  'M2: Rekursiv algoritmlar'
    M3  = 'M3',  'M3: Qidiruv algoritmlari. Xeshlash'
    M4  = 'M4',  'M4: Saralash algoritmlari'
    M5  = 'M5',  'M5: Massivlar. Bog\'langan ro\'yxatlar'
    M6  = 'M6',  'M6: Navbat, Stek va Dek'
    M7  = 'M7',  'M7: Daraxtsimon ma\'lumotlar tuzilmalari'
    M8  = 'M8',  'M8: Binar qidiruv daraxti. AVL daraxti'
    M9  = 'M9',  'M9: Heap tree'
    M10 = 'M10', 'M10: Graflar bilan ishlash algoritmlari'
    M11 = 'M11', 'M11: BFS va DFS algoritmlar'
    M12 = 'M12', 'M12: Eng qisqa yo\'l algoritmlari'


# Mavzu tartib raqami (ketma-ketlik uchun)
TOPIC_ORDER = {
    'M1': 1, 'M2': 2, 'M3': 3, 'M4': 4,
    'M5': 5, 'M6': 6, 'M7': 7, 'M8': 8,
    'M9': 9, 'M10': 10, 'M11': 11, 'M12': 12
}


class Topic(models.Model):
    """
    MTA kursi mavzusi.
    O'qituvchi tomonidan to'ldiriladi.
    Talaba ketma-ket o'rganadi (oldingi yakunlanmasa keyingisi ochilmaydi).
    """
    code = models.CharField(
        max_length=5,
        choices=TopicCode.choices,
        unique=True,
        verbose_name='Mavzu kodi'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Mavzu nomi'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Qisqacha tavsif'
    )
    order_number = models.PositiveSmallIntegerField(
        verbose_name='Tartib raqami'
    )  # 1-12
    
    # ──── DARS MATNI ────
    lecture_content = models.TextField(
        blank=True,
        verbose_name='Dars matni (HTML/Markdown)'
    )
    # Psevdokod — o'qituvchi tomonidan kiritiladi
    pseudo_code = models.TextField(
        blank=True,
        verbose_name='Psevdokod'
    )
    # Haqiqiy kod (C / C++ / Python)
    real_code = models.TextField(
        blank=True,
        verbose_name='Haqiqiy kod'
    )
    code_language = models.CharField(
        max_length=20,
        choices=[('c', 'C'), ('cpp', 'C++'), ('python', 'Python')],
        default='cpp',
        verbose_name='Kod tili'
    )
    # Vizualizatsiya turi (frontend uchun)
    visualization_type = models.CharField(
        max_length=30,
        choices=[
            ('none', 'Yo\'q'),
            ('bst', 'BST'),
            ('avl', 'AVL daraxti'),
            ('heap', 'Heap Tree'),
            ('bfs', 'BFS'),
            ('dfs', 'DFS'),
            ('sort', 'Saralash'),
            ('search', 'Qidiruv'),
        ],
        default='none',
        verbose_name='Vizualizatsiya'
    )
    
    # ──── MEDIA ────
    video_url = models.URLField(
        blank=True,
        verbose_name='Video URL (YouTube/Vimeo)'
    )
    pdf_file = models.FileField(
        upload_to='topics/pdfs/',
        blank=True,
        null=True,
        verbose_name='PDF/Slayd fayl'
    )
    
    # ──── HOLAT ────
    is_published = models.BooleanField(
        default=False,
        verbose_name='Nashr qilingan'
    )
    lecture_duration = models.PositiveSmallIntegerField(
        default=80,
        verbose_name='Dars davomiyligi (daqiqa)'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_topics',
        verbose_name='Yaratgan o\'qituvchi'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Mavzu'
        verbose_name_plural = 'Mavzular'
        ordering = ['order_number']
    
    def __str__(self):
        return f"{self.code}: {self.title}"
    
    def save(self, *args, **kwargs):
        """Tartib raqamini avtomatik belgilash"""
        if self.code and not self.order_number:
            self.order_number = TOPIC_ORDER.get(self.code, 99)
        super().save(*args, **kwargs)
    
    @property
    def previous_topic(self):
        """Oldingi mavzu"""
        if self.order_number > 1:
            return Topic.objects.filter(
                order_number=self.order_number - 1
            ).first()
        return None


class TopicProgress(models.Model):
    """
    Talabaning mavzudagi holati.
    Ketma-ketlik shu model orqali nazorat qilinadi.
    """
    
    class Status(models.TextChoices):
        LOCKED = 'locked', 'Qulflangan'
        UNLOCKED = 'unlocked', 'Ochilgan'
        IN_PROGRESS = 'in_progress', 'Jarayonda'
        COMPLETED = 'completed', 'Yakunlangan'
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='topic_progresses',
        verbose_name='Talaba'
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='student_progresses',
        verbose_name='Mavzu'
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.LOCKED,
        verbose_name='Holat'
    )
    
    # Dars ko'rilganmi?
    lesson_viewed = models.BooleanField(default=False, verbose_name='Dars ko\'rildi')
    lesson_viewed_at = models.DateTimeField(null=True, blank=True)
    
    # Qachon ochilgan / yakunlangan
    unlocked_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Mavzu holati'
        verbose_name_plural = 'Mavzu holatlari'
        unique_together = ['student', 'topic']
        ordering = ['topic__order_number']
    
    def __str__(self):
        return f"{self.student.full_name} → {self.topic.code}: {self.status}"
    
    def check_completion(self):
        """
        Mavzu yakunlanganligini tekshirish.
        Shartlar: dars ko'rilgan + topshiriq baholangan + test yechilgan
        """
        from apps.assessments.models import Submission, TestAttempt
        
        # 1. Dars ko'rilganmi?
        if not self.lesson_viewed:
            return False
        
        # 2. Amaliy topshiriq baholangan?
        has_assignment = Submission.objects.filter(
            student=self.student,
            assignment__topic=self.topic,
            grade__isnull=False  # Baho qo'yilgan
        ).exists()
        
        # 3. Test yechilgan?
        has_test = TestAttempt.objects.filter(
            student=self.student,
            test__topic=self.topic,
            completed_at__isnull=False
        ).exists()
        
        return has_assignment and has_test
