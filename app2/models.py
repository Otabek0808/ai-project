# code_compiler/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.utils import timezone
import json


# ========== SAVOL MODELI ==========
class ProgrammingQuestion(models.Model):
    DIFFICULTY = [
        ('easy', 'Oson'),
        ('medium', 'O\'rtacha'),
        ('hard', 'Qiyin'),
    ]

    question_text = models.TextField(
        validators=[MinLengthValidator(10)],
        verbose_name="Savol matni"
    )
    test_code = models.TextField(
        validators=[MinLengthValidator(20)],
        verbose_name="Test kodi (Python)",
        help_text="Foydalanuvchi Python kodini test qilish uchun test kodi"
    )
    language = models.CharField(
        max_length=20,
        default='python',
        verbose_name="Dasturlash tili",
        editable=False  # Faqat Python, o'zgartirib bo'lmaydi
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY,
        default='easy',
        verbose_name="Qiyinchilik"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='programming_questions',
        verbose_name="Yaratgan foydalanuvchi"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqt"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )

    def __str__(self):
        return f"Python Savol {self.id}: {self.question_text[:50]}..."

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Python Savol"
        verbose_name_plural = "Python Savollar"

    def save(self, *args, **kwargs):
        """Har doim Python tilida saqlash"""
        self.language = 'python'
        super().save(*args, **kwargs)


# ========== KOD YUBORISH MODELI ==========
class CodeSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('success', 'Muvaffaqiyatli'),
        ('failed', 'Muvaffaqiyatsiz'),
        ('error', 'Xatolik'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='code_submissions',
        verbose_name="Foydalanuvchi"
    )
    question = models.ForeignKey(
        ProgrammingQuestion,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name="Savol"
    )
    code = models.TextField(
        validators=[MinLengthValidator(5)],
        verbose_name="Python Kodi"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Holat"
    )
    test_result = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Test natijasi"
    )
    execution_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Ishlash vaqti (soniya)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Yaratilgan vaqt"
    )

    def __str__(self):
        return f"Python Yuborish {self.id} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Python Kod Yuborish"
        verbose_name_plural = "Python Kod Yuborishlar"

# ========== CODE COMPILER USER PROFILE ==========
class CodeCompilerProfile(models.Model):
    """Code Compiler uchun qo'shimcha profil ma'lumotlari"""
    ROLE_CHOICES = [
        ('user', 'Foydalanuvchi'),
        ('admin', 'Administrator'),
        ('superadmin', 'Super Administrator'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='code_compiler_profile',
        verbose_name="Foydalanuvchi"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name="Rol"
    )
    total_submissions = models.PositiveIntegerField(
        default=0,
        verbose_name="Jami yuborishlar"
    )
    successful_submissions = models.PositiveIntegerField(
        default=0,
        verbose_name="Muvaffaqiyatli yuborishlar"
    )
    success_rate = models.FloatField(
        default=0,
        verbose_name="Muvaffaqiyat darajasi (%)"
    )
    last_active = models.DateTimeField(
        auto_now=True,
        verbose_name="Oxirgi faollik"
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def update_statistics(self):
        """Statistikani yangilash"""
        total = self.user.code_submissions.count()
        successful = self.user.code_submissions.filter(status='success').count()

        self.total_submissions = total
        self.successful_submissions = successful
        self.success_rate = (successful / total * 100) if total > 0 else 0
        self.save()

    def get_user_info(self):
        """users app'dagi ma'lumotlarni olish"""
        try:
            profile = self.user.userprofile
            return {
                'full_name': profile.get_full_name(),
                'group': profile.group,
                'phone': profile.phone,
                'bio': profile.bio,
            }
        except:
            return {
                'full_name': self.user.username,
                'group': 'Noma\'lum',
                'phone': '',
                'bio': '',
            }

    class Meta:
        verbose_name = "Code Compiler Profil"
        verbose_name_plural = "Code Compiler Profillar"