from django.urls import path
from . import views   # 👈 SHU QATOR YO‘Q EDI

app_name = "ai_tests"

urlpatterns = [
    path('', views.ai_test_list, name='list'),
    path('generate/', views.generate_ai_test_view, name='generate'),
    path('chat/', views.ai_chat_view, name='chat'),
]