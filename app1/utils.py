# app1/utils.py
from .models import UserSubjectLevel, TestResult

def get_user_difficulty_level(user, subject):
    """Foydalanuvchining fan bo'yicha qiyinlik darajasini qaytaradi"""
    try:
        user_level = UserSubjectLevel.objects.get(user=user, subject=subject)
        return user_level.difficulty_level
    except UserSubjectLevel.DoesNotExist:
        # Agar birinchi marta bo'lsa, o'rtacha daraja qaytaramiz
        user_level = UserSubjectLevel.objects.create(
            user=user,
            subject=subject,
            difficulty_level=2
        )
        return 2

def update_user_difficulty_level(user, subject, test_result):
    """Test natijasiga asosan foydalanuvchi darajasini yangilaydi"""
    try:
        user_level = UserSubjectLevel.objects.get(user=user, subject=subject)
        user_level.update_level_based_on_result(test_result)
    except UserSubjectLevel.DoesNotExist:
        user_level = UserSubjectLevel.objects.create(
            user=user,
            subject=subject,
            difficulty_level=2
        )
        user_level.update_level_based_on_result(test_result)