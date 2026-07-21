from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Order, Profile
from .utils import send_sms


# ✅ Auto create profile for every new user
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# ✅ Save profile
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# ✅ Order SMS
@receiver(post_save, sender=Order)
def order_sms(sender, instance, created, **kwargs):

    # Safely get profile
    profile, _ = Profile.objects.get_or_create(user=instance.user)

    phone = profile.phone

    # Avoid sending SMS if phone empty
    if not phone:
        return

    try:
        # ✅ Order placed
        if created:
            send_sms(phone, f"Order {instance.txnid} placed successfully!")

        # ✅ Delivered
        elif instance.status == "Delivered":
            send_sms(phone, f"Order {instance.txnid} delivered! 🍔")
    except Exception as e:
        # SMS is a notification, not part of the order transaction — a failed
        # text (e.g. unverified number on a Twilio trial account) must never
        # cause the order itself to appear to have failed.
        print(f"SMS NOTIFICATION FAILED for order {instance.txnid}: {e}")