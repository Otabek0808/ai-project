# app2/forms.py
from django import forms
from .models import ProgrammingQuestion, CodeSubmission


class QuestionForm(forms.ModelForm):
    class Meta:
        model = ProgrammingQuestion
        fields = ['question_text', 'test_code', 'difficulty']  # language olib tashlandi
        widgets = {
            'question_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Python savol matnini batafsil yozing...',
                'style': 'resize: vertical;'
            }),
            'test_code': forms.Textarea(attrs={
                'class': 'form-control python-code',
                'rows': 10,
                'style': 'font-family: monospace; resize: vertical;',
                'placeholder': 'Python test kodini yozing. Misol:\ndef test_factorial():\n    assert factorial(5) == 120\n    print("Barcha testlar o\'tdi!")'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'question_text': 'Savol Matni',
            'test_code': 'Python Test Kodi',
            'difficulty': 'Qiyinchilik Darajasi',
        }
        help_texts = {
            'test_code': 'Foydalanuvchi Python kodini tekshirish uchun test funksiyalari',
            'question_text': 'Python savolni aniq va tushunarli yozing',
        }

    def clean_test_code(self):
        """Python test kodini tekshirish"""
        test_code = self.cleaned_data.get('test_code')

        if len(test_code.strip()) < 20:
            raise forms.ValidationError("Test kodi juda qisqa. Kamida 20 belgi bo'lishi kerak.")

        # Python kodini tekshirish (oddiy tekshiruv)
        required_keywords = ['def', 'assert']
        test_code_lower = test_code.lower()

        if not any(keyword in test_code_lower for keyword in required_keywords):
            raise forms.ValidationError(
                "Test kodida kamida bitta funksiya (def) va test (assert) bo'lishi kerak."
            )

        return test_code


class CodeSubmissionForm(forms.ModelForm):
    class Meta:
        model = CodeSubmission
        fields = ['code']
        widgets = {
            'code': forms.Textarea(attrs={
                'class': 'form-control python-code-editor',
                'rows': 20,
                'style': 'font-family: "Monaco", "Courier New", monospace; font-size: 14px; resize: vertical;',
                'placeholder': 'Python kodingizni bu yerga yozing...',
                'spellcheck': 'false',
                'id': 'python-code-editor',
                'data-language': 'python'
            }),
        }
        labels = {
            'code': 'Python Kodi',
        }
        help_texts = {
            'code': 'Python dasturlash tilida javob beradigan kodni yozing',
        }

    def clean_code(self):
        """Python kodini tekshirish"""
        code = self.cleaned_data.get('code')

        if len(code.strip()) < 5:
            raise forms.ValidationError("Kod juda qisqa. Kamida 5 belgi bo'lishi kerak.")

        # Python uchun asosiy sintaksis tekshiruvi
        python_keywords = ['def', 'import', 'print', 'return', 'if', 'for', 'while']
        code_lower = code.lower()

        # Agar kod bo'sh yoki faqat comment bo'lsa
        if code.strip().startswith('#') and len(code.strip()) < 10:
            raise forms.ValidationError("Iltimos, haqiqiy Python kodi yozing.")

        return code


class QuickQuestionForm(forms.Form):
    """Tezkor Python savol qo'shish formasi (modal uchun)"""
    question_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Python savol matni...'
        }),
        label="Python Savoli"
    )
    test_code = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control python-code',
            'rows': 6,
            'placeholder': 'Python test kodi...',
            'style': 'font-family: monospace;'
        }),
        label="Python Test Kodi"
    )
    difficulty = forms.ChoiceField(
        choices=ProgrammingQuestion.DIFFICULTY,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='easy',
        label="Qiyinchilik Darajasi"
    )

    def clean(self):
        cleaned_data = super().clean()

        # Faqat Python uchun tekshirish
        if 'test_code' in cleaned_data:
            test_code = cleaned_data['test_code']

            # Python funktsiyalari mavjudligini tekshirish
            if 'def ' not in test_code.lower():
                self.add_error('test_code', "Python test kodida kamida bitta funksiya (def) bo'lishi kerak.")

            # Kod uzunligi
            if len(test_code.strip()) < 30:
                self.add_error('test_code', "Test kodi juda qisqa. Kamida 30 belgi bo'lishi kerak.")

        return cleaned_data


# Admin uchun qo'shimcha forma
class PythonCodeTestForm(forms.Form):
    """Python kodini test qilish uchun forma"""
    python_code = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control python-code-editor',
            'rows': 15,
            'placeholder': 'Python kodini kiriting...',
            'style': 'font-family: monospace;'
        }),
        label="Python Kodi"
    )

    def clean_python_code(self):
        """Python kodini tozalash va tekshirish"""
        python_code = self.cleaned_data.get('python_code', '')

        # Xavfli importlarni tekshirish
        dangerous_imports = [
            'import os',
            'import sys',
            'import subprocess',
            'from os import',
            'from sys import',
            'from subprocess import',
            '__import__',
            'eval(',
            'exec(',
            'compile(',
            'open('
        ]

        for dangerous in dangerous_imports:
            if dangerous in python_code.lower():
                raise forms.ValidationError(
                    f"Xavfsizlik: '{dangerous}' ishlatish taqiqlangan!"
                )

        return python_code