from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
# from .forms import AIChatTestForm
from .services import generate_test_from_chat


@staff_member_required
def generate_ai_test_view(request):
    if request.method == "POST":
        form = AITestGenerateForm(request.POST)
        if form.is_valid():
            generate_ai_test(
                subject=form.cleaned_data['subject'],
                user=request.user,
                question_count=form.cleaned_data['question_count']
            )
            return redirect('ai_tests:list')
    else:
        form = AITestGenerateForm()

    return render(request, 'ai_tests/generate_test.html', {'form': form})


def ai_test_list(request):
    ai_tests = AITest.objects.select_related('test', 'subject')
    return render(request, 'ai_tests/test_list.html', {
        'ai_tests': ai_tests
    })


@staff_member_required
def ai_chat_view(request):
    if request.method == "POST":
        form = AIChatTestForm(request.POST)
        if form.is_valid():
            subject_name = form.cleaned_data['subject_name']
            question_count = form.cleaned_data.get('question_count')

            generate_test_from_chat(
                subject_name=subject_name,
                user=request.user,
                question_count=question_count
            )
            return redirect('ai_tests:list')
    else:
        form = AIChatTestForm()

    return render(request, 'ai_tests/ai_chat.html', {'form': form})