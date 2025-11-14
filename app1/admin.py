from django.contrib import admin
from .models import Subject, Document, VideoLesson, Test, Question, Answer, TestResult, TestFile, UserSubjectLevel


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'uploaded_at']


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_at']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    max_num = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'test', 'difficulty_level', 'get_answers_count']
    list_filter = ['test', 'difficulty_level']
    inlines = [AnswerInline]

    def get_answers_count(self, obj):
        return obj.answers.count()

    get_answers_count.short_description = 'Javoblar soni'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct']
    list_filter = ['is_correct', 'question__test']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'time_limit_minutes', 'question_count', 'is_active', 'uploaded_at']
    list_filter = ['subject', 'is_active', 'uploaded_at']
    list_editable = ['is_active']
    inlines = [QuestionInline]
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('subject', 'title', 'description')
        }),
        ('Test sozlamalari', {
            'fields': ('time_limit_minutes', 'question_count', 'is_active')
        }),
    )


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'test', 'score', 'total_questions', 'average_difficulty', 'percentage', 'completed_at']
    list_filter = ['test', 'completed_at']
    readonly_fields = ['average_difficulty']

    def percentage(self, obj):
        return f"{obj.percentage():.1f}%"


@admin.register(UserSubjectLevel)
class UserSubjectLevelAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'difficulty_level', 'last_updated']
    list_filter = ['subject', 'difficulty_level', 'last_updated']
    readonly_fields = ['last_updated']
    search_fields = ['user__username', 'subject__name']

    def get_difficulty_display(self, obj):
        return obj.get_difficulty_level_display()

    get_difficulty_display.short_description = 'Qiyinlik darajasi'


@admin.register(TestFile)
class TestFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'question_count', 'time_limit_minutes', 'file_format', 'is_processed', 'uploaded_at']
    list_filter = ['subject', 'is_processed', 'uploaded_at']
    actions = ['process_selected_files']
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('subject', 'title', 'description')
        }),
        ('Fayl sozlamalari', {
            'fields': ('test_file', 'file_format', 'time_limit_minutes', 'question_count')
        }),
    )

    def process_selected_files(self, request, queryset):
        for test_file in queryset:
            if not test_file.is_processed:
                success, message = test_file.process_test_file()
                if success:
                    self.message_user(request, f"'{test_file.title}' fayli muvaffaqiyatli qayta ishlandi")
                else:
                    self.message_user(request, f"'{test_file.title}' faylida xatolik: {message}", level='error')

    process_selected_files.short_description = "Tanlangan fayllarni qayta ishlash"