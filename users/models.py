from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    first_name = models.CharField(max_length=100, verbose_name='Ism', blank=True)
    last_name = models.CharField(max_length=100, verbose_name='Familiya', blank=True)
    group = models.CharField(max_length=20, verbose_name='Guruh', blank=True, help_text='Masalan: DI-11-24')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon raqam')
    bio = models.TextField(blank=True, verbose_name='Qisqacha ma\'lumot')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name} ({self.group})"
        return self.user.username

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.user.username

    class Meta:
        verbose_name = 'Foydalanuvchi profili'
        verbose_name_plural = 'Foydalanuvchi profillari'
#
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.get_or_create(user=instance)
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     if hasattr(instance, 'userprofile'):
#         instance.userprofile.save()
#     else:
#         UserProfile.objects.get_or_create(user=instance)