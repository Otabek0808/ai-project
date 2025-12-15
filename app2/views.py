import json
import os
import subprocess
import tempfile
import time
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, IntegerField
from .models import ProgrammingQuestion, CodeSubmission
from .forms import QuestionForm, CodeSubmissionForm


# ========== YORDAMCHI FUNKSIYALAR ==========

def get_user_info(user):
    """Foydalanuvchi ma'lumotlarini users app'dan olish"""
    try:
        # users app mavjudligini tekshirish
        from django.apps import apps
        if apps.is_installed('users'):
            profile = user.userprofile

            # Ma'lumotlarni xavfsiz olish
            first_name = getattr(profile, 'first_name', '')
            last_name = getattr(profile, 'last_name', '')
            full_name = f"{first_name} {last_name}".strip()

            return {
                'full_name': full_name if full_name else user.username,
                'first_name': first_name,
                'last_name': last_name,
                'group': getattr(profile, 'group', 'Guruh yo\'q'),
                'phone': getattr(profile, 'phone', ''),
                'bio': getattr(profile, 'bio', ''),
                'has_profile': True,
            }
    except:
        pass

    return {
        'full_name': user.username,
        'first_name': '',
        'last_name': '',
        'group': 'Guruh yo\'q',
        'phone': '',
        'bio': '',
        'has_profile': False,
    }


def is_code_admin(user):
    """Foydalanuvchi code admin ekanligini tekshirish"""
    return user.is_staff or user.is_superuser


def test_python_code(user_code, function_name, test_code):
    """Foydalanuvchi Python kodini test qilish - To'liq ishlaydigan versiya"""
    import subprocess, tempfile, os, time, sys, traceback

    start_time = time.time()
    result = {
        'status': 'error',
        'message': '',
        'output': '',
        'passed': False,
        'execution_time': 0
    }

    try:
        # 1. FOYDALANUVCHI KODIDA FUNKSIYA BORLIGINI TEKSHIRISH
        user_code_clean = user_code.strip()

        import re
        pattern = rf'def\s+{function_name}\s*\([^)]*\)\s*:'

        if not re.search(pattern, user_code_clean, re.MULTILINE | re.IGNORECASE):
            result['message'] = f"""
❌ XATOLIK: Kodda '{function_name}' funksiya topilmadi!

Siz quyidagicha funksiya yozishingiz kerak:
def {function_name}(...):
    # kod
    return natija

Sizning kodingiz:
{user_code[:200]}...
"""
            result['execution_time'] = round(time.time() - start_time, 2)
            return result

        # 2. KODLARNI TO'G'RI BIRLASHTIRISH
        # Avval test kodidagi indentatsiya xatolarini to'g'irlash
        test_code_clean = fix_indentation(test_code)

        full_code = f"""# -*- coding: utf-8 -*-
# FOYDALANUVCHI KODI
{user_code}

# TEST KODI
import sys
import traceback

def run_all_tests():
    \"\"\"Testlarni ishga tushirish\"\"\"
    try:
        # Testlarni ishga tushirish
{test_code_clean}

        # Agar bu yerga keldi, testlar muvaffaqiyatli
        print("\\n" + "="*60)
        print("✅ SUCCESS: Barcha testlar muvaffaqiyatli o'tdi!")
        print("="*60)
        return True

    except AssertionError as e:
        print("\\n" + "="*60)
        print("❌ TEST FAILED (AssertionError):")
        print(f"   Xato: {{e}}")
        print("="*60)
        return False

    except Exception as e:
        print("\\n" + "="*60)
        print("⚠️  RUNTIME ERROR:")
        print(f"   Xato turi: {{type(e).__name__}}")
        print(f"   Xato xabari: {{e}}")
        print("\\nStack trace:")
        traceback.print_exc()
        print("="*60)
        return False

# DASTURNI ISHGA TUSHIRISH
if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
"""

        # 3. VAQTINCHALIK FAYL YARATISH
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(full_code)
            temp_file = f.name

        # 4. KODNI ISHGA TUSHIRISH
        try:
            process = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=15,
                encoding='utf-8',
                errors='replace'
            )

            result['output'] = process.stdout
            if process.stderr:
                result['message'] = process.stderr

            if process.returncode == 0:
                result['status'] = 'success'
                result['passed'] = True
            elif process.returncode == 1:
                result['status'] = 'failed'
            else:
                result['status'] = 'error'

        except subprocess.TimeoutExpired:
            result['status'] = 'error'
            result['message'] = '⏰ Timeout: Kod 15 soniyadan ko\'proq vaqt oldi'
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f'System error: {str(e)}'
        finally:
            try:
                os.unlink(temp_file)
            except:
                pass

    except Exception as e:
        result['message'] = f'Test jarayonida xato: {str(e)}'

    result['execution_time'] = round(time.time() - start_time, 2)
    return result


def fix_indentation(code):
    """Test kodidagi indentatsiya xatolarini to'g'irlash"""
    lines = code.split('\n')
    fixed_lines = []

    for line in lines:
        stripped = line.lstrip()
        if stripped:  # Bo'sh emas
            # try, except, if, def, class dan keyin indent kerak
            fixed_lines.append('        ' + line)  # 8 ta probel (2 tab)
        else:
            fixed_lines.append(line)  # Bo'sh satr

    return '\n'.join(fixed_lines)
# app2/views.py ga qo'shing
@login_required
def test_debug(request):
    """Test qilishni debag qilish"""
    if request.method == 'POST':
        # Formadan ma'lumotlarni olish
        question_text = request.POST.get('question_text', '')
        test_code = request.POST.get('test_code', '')
        user_code = request.POST.get('user_code', '')

        # Test qilish
        result = test_python_code(user_code, test_code)

        context = {
            'question_text': question_text,
            'test_code': test_code,
            'user_code': user_code,
            'result': result,
            'debug_mode': True,
        }
        return render(request, 'app2/test_debug.html', context)

    # Boshlang'ich qiymatlar
    context = {
        'question_text': 'Ikkita sonni qo\'shuvchi funksiya yozing',
        'test_code': '''def test_add():
    # Test 1: Ijobiy sonlar
    assert add(2, 3) == 5, "2 + 3 = 5 bo'lishi kerak"

    # Test 2: Manfiy sonlar  
    assert add(-5, 10) == 5, "-5 + 10 = 5 bo'lishi kerak"

    # Test 3: Nol bilan
    assert add(0, 7) == 7, "0 + 7 = 7 bo'lishi kerak"

    print("✅ Barcha testlar muvaffaqiyatli!")

# Testni ishga tushirish
test_add()''',
        'user_code': 'def add(a, b):\n    return a + b',
    }
    return render(request, 'app2/test_debug.html', context)

# ========== ASOSIY VIEW FUNKSIYALAR ==========

@login_required
def code_practice(request):
    """Python Code Practice bosh sahifasi"""
    user_info = get_user_info(request.user)
    is_admin = is_code_admin(request.user)

    # FAQAT PYTHON savollari
    questions = ProgrammingQuestion.objects.filter(is_active=True).order_by('-created_at')

    # Qidiruv funksiyasi
    search_query = request.GET.get('q', '')
    if search_query:
        questions = questions.filter(question_text__icontains=search_query)

    # Filtrlash
    difficulty_filter = request.GET.get('difficulty', '')
    if difficulty_filter:
        questions = questions.filter(difficulty=difficulty_filter)

    context = {
        'questions': questions,
        'is_admin': is_admin,
        'search_query': search_query,
        'difficulty_filter': difficulty_filter,
        'total_questions': questions.count(),
        'user_info': user_info,
        'language': 'python',
        'title': 'Python Code Practice'
    }
    return render(request, 'app2/code_practice.html', context)


@login_required
def practice_question(request, question_id):
    """Savolni ko'rish va kod yozish"""
    question = get_object_or_404(ProgrammingQuestion, id=question_id, is_active=True)
    user_info = get_user_info(request.user)

    # Kod editori uchun boshlang'ich funksiya
    initial_code = f"def {question.function_name}({question.function_params}):\n    # Yechimni yozing\n    pass"

    if request.method == 'POST':
        user_code = request.POST.get('code', '')

        if not user_code.strip():
            messages.error(request, "Kod kiritilmagan!")
            return redirect('app2:practice_question', question_id=question_id)

        # Kodni test qilish
        result = test_python_code(
            user_code=user_code,
            function_name=question.function_name,
            test_code=question.test_code
        )

        # Saqlash
        submission = CodeSubmission.objects.create(
            user=request.user,
            question=question,
            code=user_code,
            status=result['status'],
            test_result=result,
            execution_time=result.get('execution_time')
        )

        if result['status'] == 'success':
            messages.success(request, "✅ Testlar muvaffaqiyatli o'tdi!")
        else:
            messages.warning(request, "❌ Testlar o'tmadi")

        return redirect('app2:submission_result', submission_id=submission.id)

    context = {
        'question': question,
        'initial_code': initial_code,
        'is_admin': is_code_admin(request.user),
        'user_info': user_info,
        'title': f'Python Savol: {question.question_text[:50]}...'
    }
    return render(request, 'app2/practice_question.html', context)

@login_required
def add_question(request):
    """Yangi Python savol qo'shish"""
    if not is_code_admin(request.user):
        messages.error(request, 'Sizda yangi savol qo\'shish huquqi yo\'q.')
        return redirect('app2:code_practice')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.created_by = request.user
            question.save()  # Modelning save() metodi language='python' qo'yadi
            messages.success(request, '✅ Python savoli muvaffaqiyatli qo\'shildi!')
            return redirect('app2:code_practice')
        else:
            messages.error(request, '❌ Formani to\'g\'ri to\'ldiring!')
    else:
        form = QuestionForm()

    context = {
        'form': form,
        'title': 'Yangi Python Savol Qo\'shish',
        'user_info': get_user_info(request.user),
        'language': 'python',
    }
    return render(request, 'app2/add_question.html', context)


@login_required
def submission_result(request, submission_id):
    """Yuborilgan Python kod natijasini ko'rish"""
    submission = get_object_or_404(CodeSubmission, id=submission_id, user=request.user)
    user_info = get_user_info(request.user)

    context = {
        'submission': submission,
        'title': 'Python Test Natijasi',
        'user_info': user_info,
        'language': 'python',
    }
    return render(request, 'app2/submission_result.html', context)


@login_required
def submission_history(request):
    """Foydalanuvchining barcha yuborishlari"""
    user_info = get_user_info(request.user)
    submissions = CodeSubmission.objects.filter(user=request.user) \
        .select_related('question') \
        .order_by('-created_at')

    # Statistika
    total = submissions.count()
    successful = submissions.filter(status='success').count()
    success_rate = (successful / total * 100) if total > 0 else 0

    # Qidiruv
    search_query = request.GET.get('q', '')
    if search_query:
        submissions = submissions.filter(question__question_text__icontains=search_query)

    context = {
        'submissions': submissions,
        'total': total,
        'successful': successful,
        'success_rate': round(success_rate, 1),
        'search_query': search_query,
        'title': 'Mening Python Yuborishlarim',
        'user_info': user_info,
        'language': 'python',
    }
    return render(request, 'app2/submission_history.html', context)

# app2/views.py (admin_panel funksiyasi)

@login_required
def admin_panel(request):
    """Admin panel - barcha ma'lumotlar"""
    if not is_code_admin(request.user):
        messages.error(request, 'Sizda admin panelga kirish huquqi yo\'q.')
        return redirect('app2:code_practice')

    user_info = get_user_info(request.user)

    # Savollar (faqat Python)
    questions = ProgrammingQuestion.objects.filter(language='python').order_by('-created_at')

    # Yuborishlar
    submissions = CodeSubmission.objects.all() \
        .select_related('user', 'question') \
        .order_by('-created_at')[:50]

    # Foydalanuvchilar
    users_with_info = []
    for user in User.objects.all():
        info = get_user_info(user)
        submission_count = CodeSubmission.objects.filter(user=user).count()
        successful_count = CodeSubmission.objects.filter(user=user, status='success').count()

        users_with_info.append({
            'user': user,
            'info': info,
            'submission_count': submission_count,
            'successful_count': successful_count,  # <-- Yangi qo'shildi
            'success_rate': (successful_count / submission_count * 100) if submission_count > 0 else 0,
        })

    # Statistika
    stats = {
        'total_questions': questions.count(),
        'active_questions': questions.filter(is_active=True).count(),
        'total_submissions': CodeSubmission.objects.count(),
        'successful_submissions': CodeSubmission.objects.filter(status='success').count(),
        'total_users': User.objects.count(),
        'active_today': CodeSubmission.objects.filter(
            created_at__date=timezone.now().date()
        ).count(),
    }

    context = {
        'questions': questions,
        'submissions': submissions,
        'users_with_info': users_with_info,
        'stats': stats,
        'title': 'Python Admin Panel',
        'user_info': user_info,
        'language': 'python',
    }
    return render(request, 'app2/admin_panel.html', context)

@login_required
def manage_question(request, question_id):
    """Python savolni boshqarish (o'chirish/faollashtirish)"""
    if not is_code_admin(request.user):
        messages.error(request, 'Sizda savolni boshqarish huquqi yo\'q.')
        return redirect('app2:code_practice')

    question = get_object_or_404(ProgrammingQuestion, id=question_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'toggle':
            question.is_active = not question.is_active
            question.save()
            status = 'faol' if question.is_active else 'nofaol'
            messages.success(request, f'Python savoli {status} holatga o\'zgartirildi')

        elif action == 'delete':
            question_title = question.question_text[:50]
            question.delete()
            messages.success(request, f'"{question_title}..." Python savoli o\'chirildi')

        return redirect('app2:admin_panel')

    return redirect('app2:admin_panel')


@csrf_exempt
@require_POST
@login_required
def run_test_code(request):
    """Kodni test qilish (AJAX) - yangi versiya"""
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        code = data.get('code')

        if not code or not question_id:
            return JsonResponse({
                'success': False,
                'message': 'Kod yoki savol ID\'si kiritilmagan'
            })

        question = get_object_or_404(ProgrammingQuestion, id=question_id)

        # Yangi test funksiyasini chaqirish
        result = test_python_code(
            user_code=code,
            function_name=question.function_name,
            test_code=question.test_code
        )

        return JsonResponse({
            'success': True,
            'result': result
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
def user_profile(request):
    """Foydalanuvchi profili"""
    user_info = get_user_info(request.user)

    submissions = CodeSubmission.objects.filter(user=request.user)
    total = submissions.count()
    successful = submissions.filter(status='success').count()

    # So'nggi 7 kunlik faollik
    week_ago = timezone.now() - timedelta(days=7)
    recent_submissions = submissions.filter(created_at__gte=week_ago).count()

    # Eng ko'p ishlangan savollar
    top_questions = submissions.values('question__question_text').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    context = {
        'user_info': user_info,
        'total_submissions': total,
        'successful_submissions': successful,
        'success_rate': round((successful / total * 100) if total > 0 else 0, 1),
        'recent_submissions': recent_submissions,
        'top_questions': top_questions,
        'title': 'Mening Python Profilim',
        'language': 'python',
    }
    return render(request, 'app2/user_profile.html', context)


# ========== STATIK SAHIFALAR ==========

def about(request):
    """Loyiha haqida sahifa"""
    context = {
        'title': 'Python Code Compiler Haqida',
        'language': 'python',
    }
    return render(request, 'app2/about.html', context)


def documentation(request):
    """Python dasturlash tili haqida"""
    python_info = {
        'name': 'Python',
        'version': '3.11+',
        'description': 'Python - oddiy, kuchli va ko\'p qirrali dasturlash tili',
        'features': [
            '✅ Oddiy va tushunarli sintaksis',
            '✅ OOP (Ob\'ektga yo\'naltirilgan dasturlash)',
            '✅ Keng standart kutubxona',
            '✅ Ko\'p platformali (Windows, Linux, macOS)',
            '✅ Ma\'lumotlar tahlili va ML uchun keng kutubxonalar',
            '✅ Django va Flask kabi veb-freymvorklar',
        ],
        'resources': [
            {'name': 'Python.org', 'url': 'https://python.org'},
            {'name': 'Python Documentation', 'url': 'https://docs.python.org'},
            {'name': 'Real Python', 'url': 'https://realpython.com'},
            {'name': 'Python Telegram', 'url': 'https://t.me/python_uz'},
        ],
        'examples': [
            {
                'title': 'Salom Dunyo',
                'code': 'print("Salom Dunyo!")',
                'description': 'Eng oddiy Python dasturi'
            },
            {
                'title': 'Funksiya',
                'code': 'def salom(ism):\n    print(f"Salom, {ism}!")\n\nsalom("O\'quvchi")',
                'description': 'Funksiya yaratish va chaqirish'
            },
            {
                'title': 'Ro\'yxat bilan ishlash',
                'code': 'sonlar = [1, 2, 3, 4, 5]\nkvadratlar = [x**2 for x in sonlar]\nprint(kvadratlar)',
                'description': 'List comprehension'
            },
            {
                'title': 'Faktorial hisoblash',
                'code': 'def faktorial(n):\n    if n == 0:\n        return 1\n    return n * faktorial(n-1)\n\nprint(faktorial(5))',
                'description': 'Rekursiv funksiya'
            }
        ],
        'useful_functions': [
            'print() - chop etish',
            'len() - uzunlik',
            'type() - tur',
            'str(), int(), float() - konvertatsiya',
            'range() - sonlar ketma-ketligi',
            'input() - foydalanuvchi kiritimi',
            'sum(), min(), max() - matematik funksiyalar',
            'sorted() - tartiblash',
        ]
    }

    context = {
        'python': python_info,
        'title': 'Python Dasturlash Tili',
        'language': 'python',
    }
    return render(request, 'app2/documentation.html', context)


# ========== QO'SHIMCHA VIEWLAR ==========

@login_required
def my_questions(request):
    """Foydalanuvchining qo'shgan Python savollari"""
    if not is_code_admin(request.user):
        messages.error(request, 'Sizda Python savol qo\'shish huquqi yo\'q.')
        return redirect('app2:code_practice')

    user_info = get_user_info(request.user)
    questions = ProgrammingQuestion.objects.filter(created_by=request.user).order_by('-created_at')

    context = {
        'questions': questions,
        'title': 'Mening Python Savollarim',
        'user_info': user_info,
        'language': 'python',
    }
    return render(request, 'app2/my_questions.html', context)


@login_required
def leaderboard(request):
    """Python kod yuborish reyting jadvali"""
    # Eng ko'p muvaffaqiyatli Python kod yuborgan foydalanuvchilar
    leaderboard_data = []
    users = User.objects.annotate(
        total_subs=Count('code_submissions'),
        successful_subs=Count(
            Case(
                When(code_submissions__status='success', then=1),
                output_field=IntegerField(),
            )
        )
    ).filter(total_subs__gt=0).order_by('-successful_subs')[:20]

    for user in users:
        info = get_user_info(user)
        success_rate = (user.successful_subs / user.total_subs * 100) if user.total_subs > 0 else 0

        leaderboard_data.append({
            'user': user,
            'info': info,
            'total_subs': user.total_subs,
            'successful_subs': user.successful_subs,
            'success_rate': round(success_rate, 1),
        })

    context = {
        'leaderboard': leaderboard_data,
        'title': 'Python Reyting Jadvali',
        'user_info': get_user_info(request.user),
        'language': 'python',
    }
    return render(request, 'app2/leaderboard.html', context)


# ========== QISQA YO'LLAR ==========

@login_required
def quick_submit(request, question_id):
    """Tezkor Python kod yuborish (AJAX)"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            code = request.POST.get('code', '')
            question = get_object_or_404(ProgrammingQuestion, id=question_id)

            if not code.strip():
                return JsonResponse({
                    'success': False,
                    'message': 'Python kodi bo\'sh bo\'lishi mumkin emas'
                })

            # Test qilish
            result = test_python_code(code, question.test_code)

            # Saqlash
            submission = CodeSubmission.objects.create(
                user=request.user,
                question=question,
                code=code,
                status=result['status'],
                test_result=result,
                execution_time=result.get('execution_time')
            )

            return JsonResponse({
                'success': True,
                'status': result['status'],
                'output': result['output'],
                'message': result['message'],
                'submission_id': submission.id
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })

    return JsonResponse({'success': False, 'message': 'Noto\'g\'ri so\'rov'})


# ========== QO'SHIMCHA PYTHON VIEWLAR ==========

@login_required
def python_cheatsheet(request):
    """Python cheatsheet sahifasi"""
    python_cheatsheet_data = {
        'basics': [
            {'title': 'Print', 'code': 'print("Hello World")'},
            {'title': 'Variable', 'code': 'x = 10\nname = "John"'},
            {'title': 'Input', 'code': 'name = input("Ismingiz: ")'},
            {'title': 'Comments', 'code': '# Bu comment\n"""Bu multi-line comment"""'},
        ],
        'data_types': [
            {'title': 'String', 'code': 'text = "Python"\nlen(text)  # 6'},
            {'title': 'List', 'code': 'list = [1, 2, 3]\nlist.append(4)  # [1,2,3,4]'},
            {'title': 'Tuple', 'code': 'tuple = (1, 2, 3)\ntuple[0]  # 1'},
            {'title': 'Dictionary', 'code': 'dict = {"name": "John", "age": 25}\ndict["name"]  # "John"'},
            {'title': 'Set', 'code': 'set = {1, 2, 3}\nset.add(4)  # {1,2,3,4}'},
        ],
        'control_flow': [
            {'title': 'If-Else', 'code': 'if x > 10:\n    print("Katta")\nelse:\n    print("Kichik")'},
            {'title': 'For Loop', 'code': 'for i in range(5):\n    print(i)  # 0,1,2,3,4'},
            {'title': 'While Loop', 'code': 'i = 0\nwhile i < 5:\n    print(i)\n    i += 1'},
            {'title': 'List Comprehension', 'code': 'squares = [x**2 for x in range(10)]'},
        ],
        'functions': [
            {'title': 'Function', 'code': 'def greet(name):\n    return f"Hello {name}"'},
            {'title': 'Lambda', 'code': 'square = lambda x: x**2\nsquare(5)  # 25'},
            {'title': '*args', 'code': 'def sum_all(*args):\n    return sum(args)'},
            {'title': '**kwargs', 'code': 'def print_info(**kwargs):\n    for key, value in kwargs.items():\n        print(f"{key}: {value}")'},
        ],
    }

    context = {
        'cheatsheet': python_cheatsheet_data,
        'title': 'Python Cheatsheet',
        'language': 'python',
    }
    return render(request, 'app2/python_cheatsheet.html', context)


@login_required
def python_exercises(request):
    """Python mashqlar sahifasi"""
    exercises = [
        {
            'id': 1,
            'title': 'Salom beruvchi funksiya',
            'description': 'Foydalanuvchi ismini qabul qilib, "Salom, [Ism]!" deb qaytaruvchi funksiya yozing.',
            'difficulty': 'easy',
            'hint': 'input() va print() funksiyalaridan foydalaning'
        },
        {
            'id': 2,
            'title': 'Juft sonlar',
            'description': 'Berilgan son juft yoki toq ekanligini aniqlovchi funksiya yozing.',
            'difficulty': 'easy',
            'hint': '% operatoridan foydalaning'
        },
        {
            'id': 3,
            'title': 'Faktorial hisoblash',
            'description': 'Berilgan sonning faktorialini hisoblovchi funksiya yozing.',
            'difficulty': 'medium',
            'hint': 'Rekursiya yoki for loop ishlating'
        },
        {
            'id': 4,
            'title': 'Palindrom tekshirish',
            'description': 'Berilgan so\'z palindrom (teskari o\'qilsa ham bir xil) ekanligini tekshiruvchi funksiya yozing.',
            'difficulty': 'medium',
            'hint': 'Slicing [::-1] dan foydalaning'
        },
        {
            'id': 5,
            'title': 'Tub sonlar',
            'description': 'Berilgan songacha bo\'lgan barcha tub sonlarni topuvchi funksiya yozing.',
            'difficulty': 'hard',
            'hint': 'Nested loop va sqrt() dan foydalaning'
        },
    ]

    context = {
        'exercises': exercises,
        'title': 'Python Mashqlar',
        'language': 'python',
    }
    return render(request, 'app2/python_exercises.html', context)


def python_examples(request):
    """Python misollar sahifasi"""
    examples = [
        {
            'category': 'Asosiy',
            'items': [
                {'name': 'Hello World', 'code': 'print("Hello, World!")'},
                {'name': 'O\'zgaruvchilar', 'code': 'x = 5\ny = "Hello"\nz = 3.14'},
                {'name': 'Matematik amallar', 'code': 'a = 10 + 5\nb = 10 - 5\nc = 10 * 5\nd = 10 / 5'},
            ]
        },
        {
            'category': 'Shart operatorlari',
            'items': [
                {'name': 'If-else', 'code': 'age = 18\nif age >= 18:\n    print("Katta")\nelse:\n    print("Kichik")'},
                {'name': 'Elif', 'code': 'grade = 85\nif grade >= 90:\n    print("A")\nelif grade >= 80:\n    print("B")\nelse:\n    print("C")'},
            ]
        },
        {
            'category': 'Tsikllar',
            'items': [
                {'name': 'For loop', 'code': 'for i in range(5):\n    print(i)'},
                {'name': 'While loop', 'code': 'i = 0\nwhile i < 5:\n    print(i)\n    i += 1'},
                {'name': 'List comprehension', 'code': 'squares = [x**2 for x in range(10)]'},
            ]
        },
        {
            'category': 'Funksiyalar',
            'items': [
                {'name': 'Oddiy funksiya', 'code': 'def greet(name):\n    return f"Hello {name}"'},
                {'name': 'Lambda', 'code': 'add = lambda x, y: x + y\nresult = add(5, 3)'},
            ]
        },
    ]

    context = {
        'examples': examples,
        'title': 'Python Misollar',
        'language': 'python',
    }
    return render(request, 'app2/python_examples.html', context)