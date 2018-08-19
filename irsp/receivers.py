from django.dispatch import receiver
from django.db.models import Sum
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from members.models import Paiement
from pinax.stripe.actions import customers
from pinax.stripe.models import Charge

@receiver(post_save, sender=User)
def handle_user_postsave(sender, instance, **kwargs):
    customers.create(user=instance)

@receiver(post_save, sender=Charge)
def handle_user_postsave(sender, instance, **kwargs):
    if not instance.paid:
        return
    try:
        instance.paiement.montant = instance.amount
        instance.paiement.save()
    except Paiement.DoesNotExist:
        pass

