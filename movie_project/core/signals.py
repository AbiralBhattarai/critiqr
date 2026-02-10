from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

# Default avatar URL
DEFAULT_AVATAR_URL = "https://img.icons8.com/?size=100&id=tZuAOUGm9AuS&format=png&color=000000"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # new user
        Profile.objects.create(user=instance, avatar_url=DEFAULT_AVATAR_URL)
    else:
        # existing user
        if hasattr(instance, 'profile'):
            instance.profile.save()
        #if profile doesnt exist,create.
        else:
            Profile.objects.create(user=instance, avatar_url=DEFAULT_AVATAR_URL)
