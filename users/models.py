from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_currency = models.CharField(max_length=3, default='USD')
    date_format_preference = models.CharField(max_length=20, default='MM/DD/YYYY')

    def __str__(self):
        return f"{self.user.username}'s Profile"


# Signal to create/update user profile when user is created/updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()