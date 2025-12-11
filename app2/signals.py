# code_compiler/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import CodeCompilerProfile

@receiver(post_save, sender=User)
def create_code_compiler_profile(sender, instance, created, **kwargs):
    """Yangi foydalanuvchi yaratilganda CodeCompilerProfile yaratish"""
    if created:
        CodeCompilerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_code_compiler_profile(sender, instance, **kwargs):
    """Foydalanuvchi saqlanganda profilni saqlash"""
    try:
        instance.code_compiler_profile.save()
    except:
        CodeCompilerProfile.objects.create(user=instance)