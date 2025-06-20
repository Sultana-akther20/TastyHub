from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

def cart_contents(request):
    cart_items = []
    total = 0
    item_count = 0
    cart = request.session.get('cart', {})
    
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        total += product.price * quantity
        item_count += quantity
        cart_items.append({
            'product_id': product_id,
            'quantity': quantity,
            'product': product,
        })
    
    # Convert settings values to Decimal for consistent calculation
    free_delivery_threshold = Decimal(str(settings.FREE_DELEVERY_THRESHOLD))
    standard_delivery_rate = Decimal(str(settings.STANDARD_DELEVERY)) / 100
    
    if total < free_delivery_threshold:
        delevery = total * standard_delivery_rate
        free_delevery_delta = free_delivery_threshold - total
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
        'free_delevery_threshold': free_delivery_threshold,
    }
    return context