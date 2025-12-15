# app2/forms.py
from django import forms
from .models import ProgrammingQuestion, CodeSubmission

# forms.py
from django import forms
from .models import ProgrammingQuestion, CodeSubmission


# forms.py
class QuestionForm(forms.ModelForm):
    class Meta:
        model = ProgrammingQuestion
        fields = [
            'question_text',
            'function_name',
            'function_params',
            'test_code',
            'difficulty',
            'category',
            'points',
            'is_active'
        ]
        widgets = {
            'question_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Savol matnini kiriting...'
            }),
            'function_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'qoshish, factorial, palindrom, ...'
            }),
            'function_params': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'a, b yoki n yoki text, lst ...'
            }),
            'test_code': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': f'Test kodini kiriting. {{function_name}}() funksiyasini chaqiring...',
                'id': 'test_code_field'
            }),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Matematika, String, Ro\'yxat, ...'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Placeholder'ni dinamik ravishda o'rnatish
        self.fields['test_code'].widget.attrs['placeholder'] = \
            f"Test kodini kiriting. {self.instance.function_name if self.instance.pk else 'function_name'}() funksiyasini chaqiring..."

    def clean_function_name(self):
        """Funksiya nomini validatsiya qilish"""
        name = self.cleaned_data['function_name'].strip()
        if not name.isidentifier():
            raise forms.ValidationError(
                "Funksiya nomi noto'g'ri. Faqat harf, raqam va _ belgilari bo'lishi kerak."
            )
        return name

    def clean(self):
        """Formani validatsiya qilish"""
        cleaned_data = super().clean()

        # Agar funksiya nomi va test kodi bo'lsa
        function_name = cleaned_data.get('function_name')
        test_code = cleaned_data.get('test_code')

        if function_name and test_code:
            # Test kodida funksiya nomi borligini tekshirish
            if function_name not in test_code:
                # Xatolikni qo'shamiz, lekin to'xtatmaymiz
                self.add_error('test_code',
                               f"Test kodida '{function_name}' funksiyasi chaqirilmagan. "
                               f"Test kodida {function_name}() funksiyasini chaqiring."
                               )

        return cleaned_data

class CodeSubmissionForm(forms.ModelForm):
    class Meta:
        model = CodeSubmission
        fields = ['code']
        widgets = {
            'code': forms.Textarea(attrs={
                'class': 'form-control code-editor',
                'rows': 15,
                'placeholder': 'Python kodini yozing...'
            }),
        }

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