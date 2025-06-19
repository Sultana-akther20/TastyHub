from decimal import Decimal
from django.conf import settings

def cart_contents(request):
    cart_items=[]
    total=0
    item_count=0

    if total < settings.FREE_DELEVERY_THRESHOLD:
        delevery = total * Decimal(settings.STANDARD_DELEVERY / 100)
        free_delevery_delta = settings.FREE_DELEVERY_THRESHOLD - total
    else:
        delevery = 0
        free_delevery_delta = 0
    
    grand_total = total + delevery
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'item_count': item_count,
        'delevery': delevery,
        'free_delevery_delta': free_delevery_delta,
        'grand_total': grand_total,
        'free_delevery_threshold': settings.FREE_DELEVERY_THRESHOLD,
    }

    return context