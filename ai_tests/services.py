from openai import OpenAI
from app1.models import Subject, Test, Question, Answer
from .models import AITest
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_test_from_chat(subject_name, user, question_count=None):
    if not question_count:
        question_count = 10

    subject, _ = Subject.objects.get_or_create(name=subject_name)

    prompt = f"""
    "{subject_name}" fanidan {question_count} ta test savoli tuz.

    Har bir savol:
    - 4 ta variant (A, B, C, D)
    - 1 ta to‘g‘ri javob
    - Qiyinlik darajasi (1,2,3)

    Format:
    Savol: ...
    Daraja: 2
    A) ...
    B) ...
    C) ...
    D) ...
    Javob: A
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    content = response.choices[0].message.content

    test = Test.objects.create(
        subject=subject,
        title=f"{subject.name} - AI Test",
        description="AI chat orqali yaratilgan",
        time_limit_minutes=10,
        question_count=question_count
    )

    blocks = content.split("Savol:")
    for block in blocks:
        if not block.strip():
            continue

        lines = [l.strip() for l in block.split("\n") if l.strip()]
        question_text = lines[0]
        difficulty = int(lines[1].replace("Daraja:", "").strip())

        question = Question.objects.create(
            test=test,
            text=question_text,
            difficulty_level=difficulty
        )

        options, correct = {}, None
        for line in lines[2:]:
            if line.startswith(("A)", "B)", "C)", "D)")):
                options[line[0]] = line[3:].strip()
            elif line.startswith("Javob:"):
                correct = line.replace("Javob:", "").strip()

        for key, val in options.items():
            Answer.objects.create(
                question=question,
                text=val,
                is_correct=(key == correct)
            )

    AITest.objects.create(
        subject=subject,
        test=test,
        created_by=user,
        question_count=question_count
    )
