# app2/admin.py
from django.contrib import admin
from .models import ProgrammingQuestion, CodeSubmission


@admin.register(ProgrammingQuestion)
class ProgrammingQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_preview', 'difficulty', 'is_active', 'created_by', 'created_at')
    list_filter = ('difficulty', 'is_active', 'created_at')
    search_fields = ('question_text', 'test_code')
    readonly_fields = ('language', 'created_at')
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('question_text', 'test_code', 'difficulty', 'is_active')
        }),
        ('Meta ma\'lumotlar', {
            'fields': ('language', 'created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def question_preview(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text

    question_preview.short_description = 'Savol'

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        obj.language = 'python'  # Har doim Python
        super().save_model(request, obj, form, change)


@admin.register(CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question_preview', 'status', 'execution_time', 'created_at')
    list_filter = ('status', 'created_at', 'question__difficulty')
    search_fields = ('code', 'user__username', 'question__question_text')
    readonly_fields = ('created_at', 'execution_time', 'test_result')

    def question_preview(self, obj):
        return obj.question.question_text[:50] + '...' if len(
            obj.question.question_text) > 50 else obj.question.question_text

    question_preview.short_description = 'Savol'