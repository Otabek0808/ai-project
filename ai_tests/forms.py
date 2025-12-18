from django import forms

class AIChatForm(forms.Form):
    subject_name = forms.CharField(
        label="Mavzu (fan nomi)",
        max_length=255,
        widget=forms.TextInput(attrs={
            "placeholder": "Masalan: Algoritmlar"
        })
    )
    question_count = forms.IntegerField(
        label="Savollar soni (ixtiyoriy)",
        required=False,
        min_value=5,
        max_value=30,
        widget=forms.NumberInput(attrs={
            "placeholder": "Bo‘sh bo‘lsa → 10"
        })
    )
