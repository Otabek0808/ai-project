# from django.contrib import admin
# from .models import *
#
# @admin.register(Subject)
# class SubjectAdmin(admin.ModelAdmin):
#     list_display = ['name', 'description']
#     search_fields = ['name']
#
# @admin.register(Document)
# class DocumentAdmin(admin.ModelAdmin):
#     list_display = ['title', 'subject', 'uploaded_at']
#     list_filter = ['subject', 'uploaded_at']
#     search_fields = ['title']
#
# @admin.register(VideoLesson)
# class VideoLessonAdmin(admin.ModelAdmin):
#     list_display = ['title', 'uploaded_at']
#     search_fields = ['title']
#
# @admin.register(Test)
# class TestAdmin(admin.ModelAdmin):
#     list_display = ['title', 'subject', 'uploaded_at']
#     list_filter = ['subject']
#     search_fields = ['title', 'description']
#
# @admin.register(TestResult)
# class TestResultAdmin(admin.ModelAdmin):
#     list_display = ['user', 'test', 'score', 'total_questions', 'percentage', 'completed_at']
#     list_filter = ['test', 'completed_at']
#
#     def percentage(self, obj):
#         return f"{obj.percentage():.1f}%"
#
# @admin.register(TestFile)
# class TestFileAdmin(admin.ModelAdmin):
#     list_display = ['title', 'subject', 'file_format', 'is_processed', 'uploaded_at']
#     list_filter = ['subject', 'file_format', 'is_processed', 'uploaded_at']
#     actions = ['process_files']
#
#     def process_files(self, request, queryset):
#         for test_file in queryset:
#             if not test_file.is_processed:
#                 success, message = test_file.process_test_file()
#                 if success:
#                     self.message_user(request, f"'{test_file.title}' {message}")
#                 else:
#                     self.message_user(request, f"'{test_file.title}' xatosi: {message}", level='error')
#
#     process_files.short_description = "Tanlangan test fayllarini qayta ishlash"

from django.contrib import admin
from .models import Subject, Document, VideoLesson, Test, Question, Answer, TestResult, TestFile


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'uploaded_at']


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at']


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'uploaded_at']
    list_filter = ['subject', 'uploaded_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'test', 'get_answers_count']
    list_filter = ['test']

    def get_answers_count(self, obj):
        return obj.answers.count()

    get_answers_count.short_description = 'Javoblar soni'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct']
    list_filter = ['is_correct', 'question__test']


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'score', 'total_questions', 'percentage', 'completed_at']
    list_filter = ['test', 'completed_at']

    def percentage(self, obj):
        return f"{obj.percentage():.1f}%"


@admin.register(TestFile)
class TestFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'file_format', 'is_processed', 'uploaded_at']
    list_filter = ['subject', 'is_processed', 'uploaded_at']
    actions = ['process_selected_files']

    def process_selected_files(self, request, queryset):
        for test_file in queryset:
            if not test_file.is_processed:
                success, message = test_file.process_test_file()
                if success:
                    self.message_user(request, f"'{test_file.title}' fayli muvaffaqiyatli qayta ishlandi")
                else:
                    self.message_user(request, f"'{test_file.title}' faylida xatolik: {message}", level='error')

    process_selected_files.short_description = "Tanlangan fayllarni qayta ishlash"
