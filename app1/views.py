from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from .models import *
from .forms import DocumentForm, VideoLessonForm, TestFileUploadForm, TestForm, SubjectForm, TestCreateForm
import matplotlib.pyplot as plt
import io
import base64
import json
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
from users.models import UserProfile

def home(request):
    """Bosh sahifa"""
    graphic = None

    # BARCHA foydalanuvchilar uchun videolar
    videos = VideoLesson.objects.all()
    documents = Document.objects.all()
    tests = Test.objects.all()
    users = UserProfile.objects.all()


    if request.user.is_authenticated:
        # Foydalanuvchining test natijalarini olish
        test_results = TestResult.objects.filter(user=request.user).order_by('completed_at')

        if test_results:
            # Grafik yaratish
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import io
            import base64

            plt.figure(figsize=(10, 5))

            # Testlar va ballar
            test_names = [f"Test {i + 1}" for i in range(len(test_results))]
            percentages = [result.percentage() for result in test_results]

            # Ranglar
            colors = ['blue' for p in percentages]
            # Ustunli diagramma
            bars = plt.bar(test_names, percentages, color=colors, alpha=0.7, edgecolor='black')

            # Har bir ustun ustiga foizlarni yozish
            for bar, percentage in zip(bars, percentages):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                         f'{percentage:.1f}%', ha='center', va='bottom', fontweight='bold')

            # Formatlar
            plt.title(f'Sizning Test Natijalaringiz', fontsize=14, fontweight='bold')
            plt.xlabel('Jami testlar', fontsize=12)
            plt.ylabel('Foiz (%)', fontsize=12)
            plt.xticks(rotation=0)
            plt.ylim(0, 100)
            plt.grid(True, alpha=0.3, axis='y')

            plt.tight_layout()

            # Grafikni base64 ga o'tkazish
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            graphic = base64.b64encode(image_png).decode('utf-8')
            plt.close()

    return render(request, 'app1/home.html', {
        'graphic': graphic,
        'videos': videos,
        'videos_count': videos.count(),
        'documents': documents,  # Documentlar ro'yxati
        'documents_count': documents.count(),  # Documentlar soni
        'test_count': tests.count(),
        'user_count': users.count(),
    })
def about(request):
    """Loyiha haqida sahifa"""
    return render(request, 'app1/about.html')


def documents(request):
    """Hujjatlar ro'yxati"""
    subjects = Subject.objects.prefetch_related('document_set').all()
    return render(request, 'app1/documents.html', {'subjects': subjects})


# views.py ga qo'shamiz
def subject_documents(request, subject_id):
    """Fanga oid hujjatlar ro'yxati"""
    subject = get_object_or_404(Subject, id=subject_id)
    documents = Document.objects.filter(subject=subject).order_by('-uploaded_at')

    return render(request, 'app1/subject_documents.html', {
        'subject': subject,
        'documents': documents
    })


# views.py dagi add_document funksiyasini yangilaymiz
@login_required
def add_document(request):
    """Hujjat qo'shish (faqat admin)"""
    if not request.user.is_staff:
        return redirect('home')

    # URL dan fan ID sini olish
    subject_id = request.GET.get('subject')

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material muvaffaqiyatli qo‘shildi!')
            return redirect('documents')
    else:
        initial = {}
        if subject_id:
            try:
                subject = Subject.objects.get(id=subject_id)
                initial['subject'] = subject
            except Subject.DoesNotExist:
                pass
        form = DocumentForm(initial=initial)

    return render(request, 'app1/add_document.html', {'form': form})

def video_lessons(request):
    """Video darslar ro'yxati"""
    videos = VideoLesson.objects.all()
    videos_count = videos.count()  # Sonini hisoblash

    return render(request, 'app1/video_lessons.html', {'videos': videos})


@login_required
def add_video(request):
    """Video qo'shish"""
    if request.method == 'POST':
        form = VideoLessonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video muvaffaqiyatli qo‘shildi!')
            return redirect('video_lessons')
    else:
        form = VideoLessonForm()
    return render(request, 'app1/add_video.html', {'form': form})


# -------------------- AI YORDAMCHI --------------------

def ai_chat(request):
    """AI chatbot"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            response = simple_ai_response(user_message)
            return JsonResponse({'response': response})
        except Exception:
            return JsonResponse({'response': 'Xatolik yuz berdi'})
    return render(request, 'app1/ai_chat.html')


def simple_ai_response(message):
    """AI javob generatori"""
    responses = {
        'salom': 'Salom! IT va dasturlash haqida savollaringiz bo\'lsa, javob berishga harakat qilaman.',
        'dasturlash': 'Dasturlash - bu kompyuterga turli vazifalarni bajarish uchun ko\'rsatmalar berish san\'ati.',
        'python': 'Python - bu oddiy va kuchli dasturlash tili.',
        'django': 'Django - Python da yozilgan yuqori darajadagi veb-freymvork.',
        'html': 'HTML - veb-sahifalar strukturasi uchun asosiy til.',
        'css': 'CSS - veb-sahifalarning dizaynini boshqarish uchun til.',
        'javascript': 'JavaScript - veb-sahifalarga interaktivlik qo\'shish uchun dasturlash tili.',
        'java': 'Java - "bir marta yoz, hamma joyda ishlat" tamoyiliga asoslangan til.',
        'sql': 'SQL - Ma\'lumotlar bazasiga so\'rovlar yuborish va ma\'lumotlarni boshqarish uchun til.',
        'algorithm': 'Algoritm - muammoni hal qilish uchun ketma-ket amallar to\'plami.',
        'yordam': 'Python, Django, HTML, CSS, JavaScript, Java, SQL va algoritmlar haqida yordam bera olaman.',
        'rahmat': 'Rahmat! Agar boshqa savollaringiz bo\'lsa, bemalol so\'rang.'
    }

    message_lower = message.lower()
    for key in responses:
        if key in message_lower:
            return responses[key]

    if '?' in message_lower:
        return "Qiziq savol! Men hali bu mavzuda yetarlicha ma'lumotga ega emasman."

    return "Kechirasiz, men hali bu savolga to'liq javob bera olmayman."


# -------------------- TEST TIZIMI --------------------

def tests(request):
    """Testlar ro'yxati"""
    subjects = Subject.objects.prefetch_related('test_set').all()
    return render(request, 'app1/tests.html', {'subjects': subjects})


# views.py dagi take_test funksiyasida
@login_required
def take_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)

    if not test.is_available():
        messages.error(request, "Bu test hozir faol emas")
        return redirect('tests')

    # Foydalanuvchi uchun mos savollarni olish
    questions = test.get_questions_for_user(request.user)
    total_questions = len(questions)

    if request.method == 'POST':
        # JavaScript dan kelgan sarflangan vaqt
        time_taken_str = request.POST.get('time_taken', '0')

        try:
            time_taken_seconds = int(time_taken_str)
        except (ValueError, TypeError):
            time_taken_seconds = 0

        # Vaqt chegarasini tekshirish
        max_time_seconds = test.time_limit_minutes * 60

        if time_taken_seconds > max_time_seconds:
            messages.warning(request, "Test vaqti tugadi!")
            time_taken_seconds = max_time_seconds

        score = 0
        total_questions = len(questions)

        # Javoblarni tekshirish
        for question in questions:
            user_answer_id = request.POST.get(f'question_{question.id}')
            if user_answer_id:
                try:
                    user_answer = Answer.objects.get(id=int(user_answer_id), question=question)
                    if user_answer.is_correct:
                        score += 1
                except (ValueError, Answer.DoesNotExist):
                    pass

        # Natijani saqlash
        test_result = TestResult.objects.create(
            user=request.user,
            test=test,
            score=score,
            total_questions=total_questions,
            time_taken_seconds=time_taken_seconds
        )

        # O'rtacha qiyinlik darajasini hisoblash
        test_result.calculate_average_difficulty(questions)

        # Foydalanuvchi darajasini yangilash
        from .utils import update_user_difficulty_level  # Bu yerda import qilamiz
        update_user_difficulty_level(request.user, test.subject, test_result)

        return render(request, 'app1/test_result.html', {
            'test': test,
            'score': score,
            'total_questions': total_questions,
            'percentage': (score / total_questions) * 100 if total_questions > 0 else 0,
            'time_taken_seconds': time_taken_seconds,
            'average_difficulty': test_result.average_difficulty
        })

    return render(request, 'app1/take_test.html', {
        'test': test,
        'questions': questions,
        'time_limit_seconds': test.time_limit_minutes * 60,
        'total_questions': total_questions
    })

@login_required
def submit_test(request, test_id):
    """Testni yakunlash (eski versiya)"""
    if request.method == 'POST':
        test = get_object_or_404(Test, id=test_id)
        questions = Question.objects.filter(test=test)
        score = 0

        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = Answer.objects.get(id=selected_answer_id)
                if selected_answer.is_correct:
                    score += 1

        TestResult.objects.create(
            user=request.user,
            test=test,
            score=score,
            total_questions=questions.count()
        )

        return render(request, 'app1/test_result.html', {
            'test': test,
            'score': score,
            'total': questions.count()
        })


# views.py - test_results funksiyasini yangilang
@login_required
def test_results(request):
    """Foydalanuvchi test natijalari"""
    results = TestResult.objects.filter(user=request.user).select_related('test').order_by('-completed_at')

    # Debug ma'lumotlari
    print(f"Foydalanuvchi: {request.user.username}")
    print(f"Natijalar soni: {results.count()}")

    # O'rtacha foizni hisoblaymiz
    average_percentage = 0
    if results:
        total_percentage = sum(result.percentage() for result in results)
        average_percentage = round(total_percentage / results.count(), 1)
        print(f"O'rtacha foiz: {average_percentage}%")

    return render(request, 'app1/test_results.html', {
        'results': results,
        'average_percentage': average_percentage
    })


@login_required
def test_detail(request, test_id):
    """Test tafsilotlari"""
    test = get_object_or_404(Test, id=test_id)
    return render(request, 'app1/test_detail.html', {
        'test': test,
        'status': test.get_status(),
        'is_available': test.is_available()
    })


def test_status_api(request, test_id):
    """Test holati API"""
    test = get_object_or_404(Test, id=test_id)
    data = {
        'status': test.get_status(),
        'is_available': test.is_available(),
        'time_until_start': test.time_until_start().total_seconds() if test.time_until_start() else None,
        'time_remaining': test.time_remaining().total_seconds() if test.time_remaining() else None,
        'time_limit_minutes': test.time_limit_minutes,
    }
    return JsonResponse(data)


# -------------------- ADMIN FUNKSIYALARI --------------------

def is_admin(user):
    """Admin tekshiruvi"""
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def add_subject(request):
    """Yangi fan qo'shish"""
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'"{subject.name}" fani muvaffaqiyatli qo\'shildi!')
            return redirect('tests')
    else:
        form = SubjectForm()
    return render(request, 'app1/add_subject.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def upload_test_file(request):
    """Test fayl yuklash"""
    if request.method == 'POST':
        form = TestFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            test_file = form.save()
            success, message = test_file.process_test_file()
            if success:
                messages.success(request, f"Test muvaffaqiyatli yuklandi! {message}")
            else:
                messages.warning(request, f"Fayl yuklandi, lekin xatolik: {message}")
            return redirect('tests')
    else:
        form = TestFileUploadForm()
    return render(request, 'app1/upload_test_file.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def create_test(request):
    """Qo'lda test yaratish"""
    if request.method == 'POST':
        form = TestCreateForm(request.POST)
        if form.is_valid():
            test = form.save()
            messages.success(request, f"Test '{test.title}' muvaffaqiyatli yaratildi")
            return redirect('tests')
    else:
        form = TestCreateForm()
    return render(request, 'app1/upload_test_file.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def admin_stats(request):
    """Admin statistikasi"""
    users = User.objects.all()
    return render(request, 'app1/admin_stats.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def user_stats(request, user_id):
    """Foydalanuvchi statistikasi - Ustunli diagramma bilan"""
    user = get_object_or_404(User, id=user_id)
    test_results = TestResult.objects.filter(user=user).order_by('completed_at')  # ✅ completed_at bo'yicha tartiblash

    # Eng yaxshi natijani hisoblaymiz
    best_percentage = 0
    if test_results:
        percentages = [result.percentage() for result in test_results]
        best_percentage = max(percentages)

    # Ustunli diagramma
    plt.figure(figsize=(12, 6))

    if test_results:
        # Testlar va ballar (tugatilish vaqti tartibida)
        test_names = [f"Test {i + 1}" for i in range(len(test_results))]  # ✅ Test 1, Test 2, ...
        percentages = [result.percentage() for result in test_results]

        # Ranglar - ballarga qarab
        colors = ['green' if p >= 80 else 'orange' if p >= 60 else 'red' for p in percentages]

        # Ustunli diagramma
        bars = plt.bar(test_names, percentages, color=colors, alpha=0.7, edgecolor='black')

        # Har bir ustun ustiga foizlarni yozish
        for bar, percentage in zip(bars, percentages):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     f'{percentage:.1f}%', ha='center', va='bottom', fontweight='bold')

        # Formatlar
        plt.title(f'{user.username} - Test Natijalari (Ketma-ketlik)', fontsize=14, fontweight='bold')
        plt.xlabel('Testlar (tugatilish tartibida)', fontsize=12)
        plt.ylabel('Foiz (%)', fontsize=12)
        plt.xticks(rotation=0)  # ✅ Aylantirish yo'q
        plt.ylim(0, 100)
        plt.grid(True, alpha=0.3, axis='y')

        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', alpha=0.7, label='Yaxshi (80%+)'),
            Patch(facecolor='orange', alpha=0.7, label='Qoniqarli (60-79%)'),
            Patch(facecolor='red', alpha=0.7, label='Qoniqarsiz (<60%)')
        ]
        plt.legend(handles=legend_elements)

        plt.tight_layout()

        # Grafikni base64 ga o'tkazish
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png).decode('utf-8')
        plt.close()
    else:
        graphic = None

    return render(request, 'app1/user_stats.html', {
        'user': user,
        'test_results': test_results,
        'graphic': graphic,
        'best_percentage': round(best_percentage, 1)
    })

@login_required
@user_passes_test(is_admin)
def user_profile_detail(request, user_id):
    """Foydalanuvchi profiling batafsil"""
    user = get_object_or_404(User, id=user_id)

    # Xavsiz usul bilan userprofile ni olish
    user_profile = getattr(user, 'userprofile', None)

    test_results = TestResult.objects.filter(user=user).select_related('test')

    return render(request, 'app1/user_profile_detail.html', {
        'profile_user': user,
        'user_profile': user_profile,
        'test_results': test_results
    })