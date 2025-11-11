from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ismingizni kiriting'
        }),
        label='Ism'
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Familiyangizni kiriting'
        }),
        label='Familiya'
    )
    group = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DI-11-24'
        }),
        label='Guruh',
        help_text='Guruh nomini kiriting (masalan: DI-11-24)'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        }),
        label='Email'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'group', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Foydalanuvchi nomi'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parol'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Parolni takrorlang'
        })

        # Help textlarni sozlash
        self.fields[
            'username'].help_text = 'Majburiy. 150 belgidan kam. Faqat harflar, raqamlar va @/./+/-/_ belgilari.'
        self.fields['password1'].help_text = [
            'Parolingiz boshqa shaxsiy ma\'lumotlaringizga o\'xshamasligi kerak.',
            'Parolingiz kamida 8 belgidan iborat bo\'lishi kerak.',
            'Parolingiz butunlay raqamlardan iborat bo\'lmasligi kerak.'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        print(f"🔍 DEBUG - Formdan olingan ma'lumotlar:")
        print(f"   first_name: '{self.cleaned_data['first_name']}'")
        print(f"   last_name: '{self.cleaned_data['last_name']}'")
        print(f"   group: '{self.cleaned_data['group']}'")
        print(f"   email: '{self.cleaned_data['email']}'")

        if commit:
            user.save()
            print(f"✅ DEBUG - User saqlandi:")
            print(f"   Username: '{user.username}'")
            print(f"   User.first_name: '{user.first_name}'")
            print(f"   User.last_name: '{user.last_name}'")

            # UserProfile ni yangilash
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            print(f"✅ DEBUG - UserProfile:")
            print(f"   Created: {created}")
            print(f"   Profile.first_name before: '{user_profile.first_name}'")
            print(f"   Profile.last_name before: '{user_profile.last_name}'")
            print(f"   Profile.group before: '{user_profile.group}'")

            user_profile.first_name = self.cleaned_data['first_name']
            user_profile.last_name = self.cleaned_data['last_name']
            user_profile.group = self.cleaned_data['group']
            user_profile.save()

            print(f"✅ DEBUG - Profile yangilandi:")
            print(f"   Profile.first_name after: '{user_profile.first_name}'")
            print(f"   Profile.last_name after: '{user_profile.last_name}'")
            print(f"   Profile.group after: '{user_profile.group}'")

        return user



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'group', 'phone', 'bio']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'group': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'first_name': 'Ism',
            'last_name': 'Familiya',
            'group': 'Guruh',
            'phone': 'Telefon raqam',
            'bio': 'Qisqacha ma\'lumot',
        }

