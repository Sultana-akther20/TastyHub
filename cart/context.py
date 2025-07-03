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
        try:
            product = get_object_or_404(Product, pk=product_id)
            subtotal = quantity * product.price
            total += subtotal
            item_count += quantity
            cart_items.append({
                'product_id': product_id,
                'quantity': quantity,
                'product': product,
                'subtotal': subtotal,
            })
        except Product.DoesNotExist:
            # Handle case where product no longer exists
            continue
    
    # Convert settings values to Decimal for consistent calculation
    free_delivery_threshold = Decimal(str(getattr(settings, 'FREE_DELIVERY_THRESHOLD', 50)))
    # Fixed: Use STANDARD_DELIVERY as a fixed amount, not a percentage
    standard_delivery_charge = Decimal(str(getattr(settings, 'STANDARD_DELIVERY', 5)))
    
    if total < free_delivery_threshold:
        delivery = standard_delivery_charge  # Fixed: Use fixed charge instead of percentage
        free_delivery_delta = free_delivery_threshold - total
    else:
        delivery = 0
        free_delivery_delta = 0
    
    grand_total = total + delivery
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'item_count': item_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'grand_total': grand_total,
        'free_delivery_threshold': free_delivery_threshold,
    }
    return context