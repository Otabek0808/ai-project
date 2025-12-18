from django.db import models
from django.contrib.auth.models import User
from app1.models import Subject, Test, Question, Answer


class AITest(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.OneToOneField(Test, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    question_count = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Test - {self.subject.name}"
