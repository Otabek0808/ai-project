# admin.py
from django.contrib import admin
from .models import ProgrammingQuestion, CodeSubmission, CodeCompilerProfile


@admin.register(ProgrammingQuestion)
class ProgrammingQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'function_name', 'question_preview', 'difficulty', 'category', 'points', 'is_active',
                    'created_by', 'created_at')
    list_filter = ('difficulty', 'category', 'is_active', 'created_at')
    search_fields = ('question_text', 'function_name', 'category')
    list_editable = ('is_active', 'points')
    readonly_fields = ('language', 'created_at')
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('question_text', 'function_name', 'function_params', 'difficulty')
        }),
        ('Test qilish', {
            'fields': ('test_code', 'category', 'points')
        }),
        ('Qo\'shimcha', {
            'fields': ('language', 'created_by', 'is_active', 'created_at')
        }),
    )

    def question_preview(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text

    question_preview.short_description = 'Savol'

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Yangi yaratilayotganda
            obj.created_by = request.user
        super().save_model(request, obj, form, change)