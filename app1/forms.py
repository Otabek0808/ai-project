from django import forms
from .models import VideoLesson, Document, TestFile, Subject


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'subject', 'file']



class VideoLessonForm(forms.ModelForm):
    class Meta:
        model = VideoLesson
        fields = ['title', 'iframe_code', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Video nomini kiriting'}),
            'iframe_code': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'YouTube yoki boshqa iframe kodini kiriting'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': "Video haqida qisqacha ma'lumot"}),
        }


from django import forms
from django.utils import timezone
from .models import TestFile, Test
import datetime

from django import forms
from .models import TestFile, Test


class TestFileUploadForm(forms.ModelForm):
    class Meta:
        model = TestFile
        fields = [
            'subject', 'title', 'description', 'test_file',
            'time_limit_minutes', 'question_count'  # Vaqt chegarasi va savollar soni
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'test_file': forms.FileInput(attrs={'class': 'form-control'}),
            'time_limit_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': '30'
            }),
            'question_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 200,
                'placeholder': '25'
            }),
        }
        help_texts = {
            'time_limit_minutes': 'Testni ishlash uchun berilgan maksimal vaqt (daqiqada)',
            'question_count': 'Testdagi savollar soni (maksimum 200)',
        }


class TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        time_limit = kwargs.pop('time_limit', 30)
        super(TestForm, self).__init__(*args, **kwargs)

        self.time_limit_minutes = time_limit

        for question in questions:
            answers = question.answers.all()
            choices = [(answer.id, answer.text) for answer in answers]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                label=question.text,
                required=True
            )


class TestCreateForm(forms.ModelForm):
    """Testni qo'lda yaratish formasi"""

    class Meta:
        model = Test
        fields = [
            'subject', 'title', 'description',
            'time_limit_minutes', 'question_count', 'is_active'  # Savollar soni qo'shildi
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'time_limit_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'question_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 200,
                'placeholder': '25'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'question_count': 'Testdagi savollar soni (maksimum 200)',
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg border-primary',
                'placeholder': 'Fan nomini kiriting...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control border-success',
                'rows': 4,
                'placeholder': 'Fan haqida tavsif...'
            }),
        }
        labels = {
            'name': 'Fan Nomi',
            'description': 'Fan Tavsifi'
        }