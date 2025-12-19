from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class AITest(models.Model):
    """AI tomonidan yaratilgan test"""
    topic = models.CharField(max_length=255, verbose_name="Test mavzusi")
    prompt = models.TextField(verbose_name="AI so'rovi", blank=True)
    ai_response = models.TextField(verbose_name="AI javobi", blank=True)
    questions_data = models.JSONField(verbose_name="Savollar ma'lumoti", default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "AI Test"
        verbose_name_plural = "AI Testlar"

    def __str__(self):
        return f"AI Test: {self.topic}"

    def create_test_from_ai_response(self):
        """AI javobidan test yaratish"""
        try:
            # JSON formatni tahlil qilish
            response_text = self.ai_response

            # JSON qismini ajratib olish
            json_str = None

            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].strip()
            elif response_text.strip().startswith('[') and response_text.strip().endswith(']'):
                json_str = response_text.strip()

            if not json_str:
                # Agar JSON topilmasa, qo'lda tahlil qilish
                questions_data = []
                lines = response_text.split('\n')

                current_question = None
                current_options = []
                current_correct = None

                for line in lines:
                    line = line.strip()
                    if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                        if current_question and current_options:
                            questions_data.append({
                                'question': current_question,
                                'options': current_options,
                                'correct': current_correct or 0
                            })

                        # Yangi savol
                        parts = line.split('.', 1)
                        if len(parts) > 1:
                            current_question = parts[1].strip()
                            current_options = []
                            current_correct = None
                    elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                        option_text = line[2:].strip().replace('✓', '').replace('(to\'g\'ri)', '').strip()
                        current_options.append(option_text)
                        if '✓' in line or '(to\'g\'ri)' in line.lower():
                            current_correct = len(current_options) - 1

                if current_question and current_options:
                    questions_data.append({
                        'question': current_question,
                        'options': current_options,
                        'correct': current_correct or 0
                    })

                self.questions_data = questions_data
                self.save()
                return True, f"{len(questions_data)} ta savol yaratildi"

            else:
                # JSON dan foydalanish
                questions_data = json.loads(json_str)
                self.questions_data = questions_data
                self.save()
                return True, f"{len(questions_data)} ta savol yaratildi"

        except Exception as e:
            import traceback
            print(f"Xatolik: {e}")
            print(traceback.format_exc())
            return False, f"Xatolik: {str(e)}"


class TestAttempt(models.Model):
    """Foydalanuvchi test natijasi"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ai_test = models.ForeignKey(AITest, on_delete=models.CASCADE)
    score = models.IntegerField(default=0, verbose_name="To'g'ri javoblar")
    total_questions = models.IntegerField(default=10, verbose_name="Jami savollar")
    time_taken_seconds = models.IntegerField(default=0, verbose_name="Sarflangan vaqt")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.ai_test.topic}: {self.score}/{self.total_questions}"

    def percentage(self):
        if self.total_questions > 0:
            return round((self.score / self.total_questions) * 100, 1)
        return 0