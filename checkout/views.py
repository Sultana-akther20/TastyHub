from django.shortcuts import render,redirect, reverse
from django.contrib import messages

from .forms import OrderForm

# Create your views here.
def checkout(request):
    """Handle the checkout process."""
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty. Please add items before checking out.')
        return redirect(reverse('products'))
    
    order_form = OrderForm()
    templates = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51RcvRlID5KfeNNAenv11oDIvdPOo5YDTeEuRBS4gIBeQEaMTIMRSsTkP9LfDLUu9cmtrppOPWRSwTHVGeVVaQzJm006OJjUUQx',
        'client_secret': 'test secret',
    }   

    return render(request, templates, context)