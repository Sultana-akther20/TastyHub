from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import OrderItem

@receiver(post_save, sender=OrderItem)
def update_on_save(sender, instance, created, **kwargs):
    """Update the order total when an OrderItem is created/updated."""
    instance.order.update_total()

@receiver(post_delete, sender=OrderItem)
def delete_order_item(sender, instance, **kwargs):
    """Update the order total when an OrderItem is deleted."""
    instance.order.update_total()
