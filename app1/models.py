from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
import os
import random


# -------------------- Subject va Document --------------------
class Subject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    title = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='documents/')

    def __str__(self):
        return self.title


# -------------------- VideoLesson --------------------
# models.py - VideoLesson modeliga qo'shing
class VideoLesson(models.Model):
    title = models.CharField(max_length=255)
    iframe_code = models.TextField()  # YouTube iframe kodi
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Subject qo'shing (ixtiyoriy, ForeignKey yoki CharField)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,  # yoki CASCADE
        null=True,
        blank=True,
        verbose_name="Fan"
    )

    def __str__(self):
        return self.title


# -------------------- Test, Question, Answer --------------------
class Test(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    # Faqat vaqt chegarasi
    time_limit_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name="Test vaqti (daqiqa)",
        help_text="Testni ishlash uchun berilgan maksimal vaqt"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol",
        help_text="Test hozir ishlash uchun mavjudmi"
    )

    # Yangi maydon: testdagi savollar soni
    question_count = models.PositiveIntegerField(
        default=25,
        verbose_name="Savollar soni",
        help_text="Testdagi umumiy savollar soni"
    )

    def is_available(self):
        """Test hozir ishlash uchun mavjudmi"""
        return self.is_active

    def get_status(self):
        """Test holatini qaytaradi"""
        if not self.is_active:
            return "nofaol"
        else:
            return "faol"

    def get_questions_for_user(self, user):
        """Foydalanuvchi uchun mos savollarni qaytaradi"""
        from .utils import get_user_difficulty_level  # Circular importni oldini olish

        # Foydalanuvchining oxirgi natijasiga qarab qiyinlik darajasini olish
        difficulty_level = get_user_difficulty_level(user, self.subject)

        # Savollarni qiyinlik darajasi bo'yicha filtrlash
        questions = self.questions.all()

        if difficulty_level == 1:  # Oson
            easy_questions = questions.filter(difficulty_level=1)
            if easy_questions.count() >= 25:
                return random.sample(list(easy_questions), 25)
            else:
                # Agar oson savollar yetmasa, barcha savollardan tanlaymiz
                return random.sample(list(questions), min(25, questions.count()))

        elif difficulty_level == 2:  # O'rtacha
            medium_questions = questions.filter(difficulty_level=2)
            if medium_questions.count() >= 25:
                return random.sample(list(medium_questions), 25)
            else:
                # Agar o'rtacha savollar yetmasa, oson va qiyin savollarni qo'shamiz
                all_questions = list(questions)
                return random.sample(all_questions, min(25, len(all_questions)))

        elif difficulty_level == 3:  # Qiyin
            hard_questions = questions.filter(difficulty_level=3)
            if hard_questions.count() >= 25:
                return random.sample(list(hard_questions), 25)
            else:
                # Agar qiyin savollar yetmasa, barcha savollardan tanlaymiz
                return random.sample(list(questions), min(25, questions.count()))

        # Agar birinchi marta bo'lsa yoki difficulty_level aniqlanmagan bo'lsa
        return random.sample(list(questions), min(25, questions.count()))

    def __str__(self):
        return f"{self.title} ({self.time_limit_minutes} daqiqa)"


class Question(models.Model):
    DIFFICULTY_LEVELS = (
        (1, 'Oson'),
        (2, 'O\'rtacha'),
        (3, 'Qiyin'),
    )

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    # Yangi maydon: savolning qiyinlik darajasi
    difficulty_level = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_LEVELS,
        default=2,
        verbose_name="Qiyinlik darajasi"
    )

    def __str__(self):
        return f"{self.text[:50]} (Daraja: {self.difficulty_level})"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'To‘g‘ri' if self.is_correct else 'Noto‘g‘ri'})"


# -------------------- TestResult --------------------
class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    total_questions = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)
    time_taken_seconds = models.PositiveIntegerField(
        default=0,
        verbose_name="Sarflangan vaqt (soniya)",
        help_text="Foydalanuvchi testni ishlashga sarflagan vaqt"
    )

    # Yangi maydon: o'rtacha qiyinlik darajasi
    average_difficulty = models.FloatField(
        default=0,
        verbose_name="O'rtacha qiyinlik",
        help_text="Testdagi savollarning o'rtacha qiyinlik darajasi"
    )

    def percentage(self):
        if self.total_questions > 0:
            return (self.score / self.total_questions) * 100
        return 0

    def get_time_taken_display(self):
        """Sarflangan vaqtni daqiqa:soniya formatida ko'rsatish"""
        minutes = self.time_taken_seconds // 60
        seconds = self.time_taken_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def calculate_average_difficulty(self, questions):
        """Testdagi savollarning o'rtacha qiyinlik darajasini hisoblaydi"""
        if questions:
            total_difficulty = sum(question.difficulty_level for question in questions)
            self.average_difficulty = total_difficulty / len(questions)
            self.save()

    def __str__(self):
        return f"{self.user.username} - {self.test.title} - {self.score}/{self.total_questions}"


# -------------------- Yangi model: UserSubjectLevel --------------------
class UserSubjectLevel(models.Model):
    """Foydalanuvchining har bir fan bo'yicha darajasini saqlaydi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    difficulty_level = models.PositiveSmallIntegerField(
        choices=Question.DIFFICULTY_LEVELS,
        default=2,
        verbose_name="Qiyinlik darajasi"
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'subject']
        verbose_name = "Foydalanuvchi fan darajasi"
        verbose_name_plural = "Foydalanuvchi fan darajalari"

    def __str__(self):
        return f"{self.user.username} - {self.subject.name} (Daraja: {self.difficulty_level})"

    def update_level_based_on_result(self, test_result):
        """Test natijasiga asosan foydalanuvchi darajasini yangilaydi"""
        percentage = test_result.percentage()

        if percentage >= 80:  # A'lo natija
            self.difficulty_level = min(3, self.difficulty_level + 1)  # Qiyinroq
        elif percentage >= 60:  # Yaxshi natija
            # O'zgarishsiz qoladi yoki biroz oshadi
            self.difficulty_level = min(3, self.difficulty_level)
        elif percentage >= 40:  # Qoniqarli natija
            self.difficulty_level = max(1, self.difficulty_level - 0.5)  # Biroz osonroq
        else:  # Qoniqarsiz natija
            self.difficulty_level = max(1, self.difficulty_level - 1)  # Osonroq

        self.difficulty_level = round(self.difficulty_level)
        self.save()


class TestFile(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    test_file = models.FileField(upload_to='test_files/')
    file_format = models.CharField(max_length=10, default='txt')

    # Faqat vaqt chegarasi
    time_limit_minutes = models.PositiveIntegerField(
        default=30,
        verbose_name="Test vaqti (daqiqa)"
    )

    # Yangi maydon: testdagi savollar soni
    question_count = models.PositiveIntegerField(
        default=25,
        verbose_name="Savollar soni"
    )

    is_processed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def process_test_file(self):
        """
        .txt fayl formatini qayta ishlaydi
        Endi faylda savolning qiyinlik darajasi ham bo'ladi
        Format: Savol: [savol matni] | Daraja: [1,2,3]
        """
        try:
            # Faylni o'qish
            file_path = self.test_file.path
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"Fayl mazmuni: {content}")  # Debug

            # Test nomi fayl nomidan olinadi
            test_title = self.title or os.path.splitext(os.path.basename(file_path))[0]

            # Test yaratish
            test = Test.objects.create(
                subject=self.subject,
                title=test_title,
                description=f"Fayldan yuklangan: {self.test_file.name}",
                time_limit_minutes=self.time_limit_minutes,
                question_count=self.question_count
            )

            # Savollarni ajratib olish
            questions_blocks = content.split('Savol:')
            print(f"Savol bloklari soni: {len(questions_blocks)}")  # Debug

            question_count = 0
            answer_count = 0

            for block in questions_blocks:
                if not block.strip():
                    continue

                lines = [line.strip() for line in block.split('\n') if line.strip()]
                if not lines:
                    continue

                # Birinchi qator savol matni va qiyinlik darajasi
                first_line = lines[0]
                difficulty_level = 2  # Default o'rtacha

                # Qiyinlik darajasini ajratib olish
                if '| Daraja:' in first_line:
                    question_parts = first_line.split('| Daraja:')
                    question_text = question_parts[0].strip()
                    try:
                        difficulty_level = int(question_parts[1].strip())
                    except (ValueError, IndexError):
                        difficulty_level = 2
                else:
                    question_text = first_line

                print(f"Savol: {question_text}, Daraja: {difficulty_level}")  # Debug

                question = Question.objects.create(
                    test=test,
                    text=question_text,
                    difficulty_level=difficulty_level
                )
                question_count += 1

                # Variantlarni qayta ishlash
                options = {}
                correct_answer = None

                for line in lines[1:]:
                    print(f"Qator: {line}")  # Debug
                    if line.startswith('A) '):
                        options['A'] = line[3:].strip()
                    elif line.startswith('B) '):
                        options['B'] = line[3:].strip()
                    elif line.startswith('C) '):
                        options['C'] = line[3:].strip()
                    elif line.startswith('D) '):
                        options['D'] = line[3:].strip()
                    elif line.startswith('Javob: '):
                        correct_answer = line[7:].strip()

                print(f"Variantlar: {options}")  # Debug
                print(f"To'g'ri javob: {correct_answer}")  # Debug

                # Javoblarni saqlash
                for option_key, option_text in options.items():
                    Answer.objects.create(
                        question=question,
                        text=option_text,
                        is_correct=(option_key == correct_answer)
                    )
                    answer_count += 1

            self.is_processed = True
            self.save()
            return True, f"Test muvaffaqiyatli yaratildi. {question_count} ta savol, {answer_count} ta javob qo'shildi."

        except Exception as e:
            import traceback
            print(f"Xato: {traceback.format_exc()}")  # Debug
            return False, f"Xatolik: {str(e)}"