from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from .forms import CustomUserCreationForm, UserProfileForm
from app1.models import TestResult
from .models import UserProfile


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # DEBUG: Konsolga chiqaramiz
            print(f"Yangi foydalanuvchi: {user.username}")
            print(f"User first_name: {user.first_name}")
            print(f"User last_name: {user.last_name}")

            # Profilni tekshiramiz
            try:
                profile = user.userprofile
                print(f"Profile first_name: {profile.first_name}")
                print(f"Profile last_name: {profile.last_name}")
                print(f"Profile group: {profile.group}")
            except Exception as e:
                print(f"Profil xatosi: {e}")

            # Foydalanuvchi avtomatik tizimga kirishi
            from django.contrib.auth import login
            login(request, user)
            messages.success(request, f'Xush kelibsiz, {user.first_name}! Ro\'yxatdan muvaffaqiyatli o\'tdingiz.')
            return redirect('home')
        else:
            print("Form noto'g'ri:")
            print(form.errors)
            messages.error(request, 'Iltimos, formani to\'g\'ri to\'ldiring.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    # UserProfile ni olish yoki yaratish
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Agar userprofile mavjud bo'lmasa, yangisini yarat
        user_profile = UserProfile.objects.create(user=request.user)
        messages.info(request, "Sizning profilingiz yaratildi!")

    # Test natijalarini olish
    test_results = TestResult.objects.filter(user=request.user)

    # Eng yaxshi natijani hisoblash
    best_percentage = 0
    if test_results:
        best_percentage = max([result.percentage() for result in test_results])

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil ma\'lumotlari muvaffaqiyatli yangilandi!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'users/profile.html', {
        'user_profile': user_profile,
        'form': form,
        'test_results': test_results,
        'best_percentage': best_percentage
    })

@require_POST
@csrf_protect
def custom_logout(request):
    logout(request)
    return redirect('home')