from django import forms
from .models import AITest


class SimpleAITestForm(forms.Form):
    """Soddalashtirilgan AI test formasi"""
    topic = forms.CharField(
        max_length=255,
        label="Test mavzusi",
        widget=forms.TextInput(attrs={
            'placeholder': 'Misol: Python funksiyalari, Django models, SQL queries...',
            'class': 'form-control',
            'autocomplete': 'off'
        })
    )

    prompt = forms.CharField(
        required=False,
        label="Qo'shimcha so'rov (ixtiyoriy)",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Misol: Savollar aniq va tushunarli bo\'lsin...',
            'autocomplete': 'off'
        })
    )