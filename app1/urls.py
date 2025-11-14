# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('', views.home, name='home'),
#     path('about/', views.about, name='about'),
#     path('documents/', views.documents, name='documents'),
#     path('video-lessons/', views.video_lessons, name='video_lessons'),
#     path('ai-chat/', views.ai_chat, name='ai_chat'),
#     path('tests/', views.tests, name='tests'),
#     path('test/<int:test_id>/', views.take_test, name='take_test'),
#     path('test/<int:test_id>/submit/', views.submit_test, name='submit_test'),
#     path('admin-stats/', views.admin_stats, name='admin_stats'),
#     path('user-stats/<int:user_id>/', views.user_stats, name='user_stats'),
#     path('user-profile/<int:user_id>/', views.user_profile_detail, name='user_profile_detail'),
#     path('upload-test-file/', views.upload_test_file, name='upload_test_file'),  # Bu URL mavjud bo'lishi kerak
#     path('documents/add/', views.add_document, name='add_document'),
#     path('video/add/', views.add_video, name='add_video'),
#     path('test-results/', views.test_results, name='test_results'),  # Bu yo'q bo'lsa qo'shing
#     path('add-subject/', views.add_subject, name='add_subject'),
#
# ]
from django.urls import path
from . import views

urlpatterns = [
    # Asosiy sahifalar
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('documents/', views.documents, name='documents'),
    path('add-document/', views.add_document, name='add_document'),
    path('videos/', views.video_lessons, name='video_lessons'),
    path('add-video/', views.add_video, name='add_video'),
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('subject/<int:subject_id>/documents/', views.subject_documents, name='subject_documents'),

    # Test tizimi
    path('tests/', views.tests, name='tests'),
    path('test/<int:test_id>/', views.take_test, name='take_test'),
    path('test/<int:test_id>/submit/', views.submit_test, name='submit_test'),
    path('my-results/', views.test_results, name='test_results'),
    path('test/<int:test_id>/detail/', views.test_detail, name='test_detail'),
    path('api/test/<int:test_id>/status/', views.test_status_api, name='test_status_api'),

    # Admin funksiyalari
    path('add-subject/', views.add_subject, name='add_subject'),
    path('upload-test-file/', views.upload_test_file, name='upload_test_file'),
    path('create-test/', views.create_test, name='create_test'),
    path('admin-stats/', views.admin_stats, name='admin_stats'),
    path('user-stats/<int:user_id>/', views.user_stats, name='user_stats'),
    path('user-profile/<int:user_id>/', views.user_profile_detail, name='user_profile_detail'),
]