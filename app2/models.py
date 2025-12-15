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
        verbose_name="Savol matni",
        help_text="Savolning to'liq matnini kiriting"
    )

    function_name = models.CharField(
        max_length=50,
        default='solution',
        verbose_name="Funksiya nomi",
        help_text="Foydalanuvchi yozishi kerak bo'lgan funksiya nomi (masalan: 'qoshish', 'factorial')"
    )

    function_params = models.CharField(
        max_length=200,
        default='a, b',
        verbose_name="Funksiya parametrlari",
        help_text="Funksiya parametrlarini kiriting (masalan: 'a, b', 'n', 'text')"
    )

    test_code = models.TextField(
        validators=[MinLengthValidator(20)],
        verbose_name="Python Test Kodi",
        help_text=f"""Foydalanuvchi funksiyasini test qilish uchun Python kodi.
Test kodida {function_name}() funksiyasini chaqiring va assert yordamida tekshiring.

MASALAN:
result = {function_name}(5, 3)
assert result == 8, f"5 + 3 = 8 bo'lishi kerak, lekin {{result}} qaytdi"
print("✅ Test muvaffaqiyatli!")"""
    )

    language = models.CharField(
        max_length=20,
        default='python',
        verbose_name="Dasturlash tili",
        editable=False
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY,
        default='easy',
        verbose_name="Qiyinchilik darajasi"
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

    # Yangi maydonlar
    category = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Kategoriya",
        help_text="Savol kategoriyasi (masalan: Matematika, String, Ro'yxat)"
    )

    points = models.PositiveIntegerField(
        default=10,
        verbose_name="Ball",
        help_text="Savolning ball qiymati"
    )

    def __str__(self):
        return f"Python Savol {self.id}: {self.function_name}() - {self.question_text[:50]}..."

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Python Savol"
        verbose_name_plural = "Python Savollar"

    def save(self, *args, **kwargs):
        """Har doim Python tilida saqlash"""
        self.language = 'python'
        super().save(*args, **kwargs)

    def get_initial_code(self):
        """Foydalanuvchi uchun boshlang'ich kod"""
        return f"def {self.function_name}({self.function_params}):\n    # Yechimni yozing\n    pass"

    def clean(self):
        """Modelni validatsiya qilish"""
        from django.core.exceptions import ValidationError

        # Funksiya nomini tekshirish
        if not self.function_name.isidentifier():
            raise ValidationError({
                'function_name': "Funksiya nomi noto'g'ri. Faqat harf, raqam va _ belgilari bo'lishi kerak."
            })

        # Test kodida funksiya nomi ishlatilganligini tekshirish (faqat warning sifatida)
        # Bu required emas, chunki admin keyinroq o'zgartirishi mumkin
        if self.function_name not in self.test_code:
            # Faqat ogohlantirish, xato emas
            pass  # Xatolik chiqarmaymiz

        return super().clean()

    @property
    def function_signature(self):
        """Funksiya imzosi"""
        return f"def {self.function_name}({self.function_params}):"

    @property
    def difficulty_badge_color(self):
        """Qiyinchilik darajasi uchun badge rangi"""
        colors = {
            'easy': 'success',
            'medium': 'warning',
            'hard': 'danger'
        }
        return colors.get(self.difficulty, 'secondary')

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