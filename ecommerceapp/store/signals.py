# store/signals.py
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Customer

@receiver(post_save, sender=User)
def create_customer_for_new_user(sender, instance, created, **kwargs):
    if created:
        # Automatically create a Customer linked to this User
        Customer.objects.create(
            user=instance,
            first_name=instance.first_name or instance.username,
            last_name=instance.last_name or "",
            email=instance.email,
            phone_number=""
        )
