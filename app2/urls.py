# app2/urls.py
from django.urls import path
from . import views

app_name = 'app2'

urlpatterns = [
    # Asosiy sahifalar
    path('', views.code_practice, name='code_practice'),
    path('about/', views.about, name='about'),
    path('documentation/', views.documentation, name='documentation'),

    # Python mashqlar va misollar
    path('python-cheatsheet/', views.python_cheatsheet, name='python_cheatsheet'),
    path('python-exercises/', views.python_exercises, name='python_exercises'),
    path('python-examples/', views.python_examples, name='python_examples'),

    # Python savol bilan ishlash
    path('question/<int:question_id>/', views.practice_question, name='practice_question'),
    path('add-question/', views.add_question, name='add_question'),
    path('my-questions/', views.my_questions, name='my_questions'),
    path('manage-question/<int:question_id>/', views.manage_question, name='manage_question'),

    # Python yuborishlar
    path('submission/<int:submission_id>/', views.submission_result, name='submission_result'),
    path('submission-history/', views.submission_history, name='submission_history'),
    path('quick-submit/<int:question_id>/', views.quick_submit, name='quick_submit'),

    # Profil va reyting
    path('profile/', views.user_profile, name='user_profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),

    # Admin
    path('admin-panel/', views.admin_panel, name='admin_panel'),

    # AJAX yo'llari
    path('run-test/', views.run_test_code, name='run_test'),
]