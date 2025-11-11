from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
import os


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
class VideoLesson(models.Model):
    title = models.CharField(max_length=255)
    iframe_code = models.TextField()  # YouTube iframe kodi
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

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

    def is_available(self):
        """Test hozir ishlash uchun mavjudmi"""
        return self.is_active

    def get_status(self):
        """Test holatini qaytaradi"""
        if not self.is_active:
            return "nofaol"
        else:
            return "faol"

    def __str__(self):
        return f"{self.title} ({self.time_limit_minutes} daqiqa)"


class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return self.text[:50]  # Birinchi 50 belgini ko'rsatish


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

    def percentage(self):
        if self.total_questions > 0:
            return (self.score / self.total_questions) * 100
        return 0

    def get_time_taken_display(self):
        """Sarflangan vaqtni daqiqa:soniya formatida ko'rsatish"""
        minutes = self.time_taken_seconds // 60
        seconds = self.time_taken_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def __str__(self):
        return f"{self.user.username} - {self.test.title} - {self.score}/{self.total_questions}"


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

    is_processed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def process_test_file(self):
        """
        .txt fayl formatini qayta ishlaydi
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
                time_limit_minutes=self.time_limit_minutes
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

                # Birinchi qator savol matni
                question_text = lines[0]
                print(f"Savol: {question_text}")  # Debug

                question = Question.objects.create(test=test, text=question_text)
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