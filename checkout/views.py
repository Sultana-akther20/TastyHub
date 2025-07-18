from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.db import transaction
from cart.context import cart_contents
from .forms import OrderForm
from .models import Order, OrderItem
from products.models import Product
import stripe
import json
import logging

logger = logging.getLogger(__name__)

@require_POST
def cache_checkout_data(request):
    """Cache checkout data in the payment intent metadata"""
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Get cart data
        cart = request.session.get('cart', {})
        
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': json.dumps(cart),
            'save_info': request.POST.get('save_info'),
            'username': request.user.username if request.user.is_authenticated else 'Anonymous',
        })
        return HttpResponse(status=200)
    except Exception as e:
        logger.error(f"Error caching checkout data: {e}")
        messages.error(request, 'Your payment could not be processed. Please try again.')
        return HttpResponse(content=str(e), status=400)

def checkout(request):
    """Handle the checkout process."""
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    
    if not stripe_publishable_key or not stripe_secret_key:
        messages.error(request, 'Stripe configuration is missing. Please contact support.')
        return redirect(reverse('view_cart'))
    
    if request.method == 'POST':
        logger.info("Processing POST request for checkout")
        cart = request.session.get('cart', {})
        
        if not cart:
            logger.warning("Cart is empty during checkout POST")
            messages.error(request, 'Your cart is empty.')
            return redirect(reverse('products'))
        
        # Get the client_secret and extract payment intent ID
        client_secret = request.POST.get('client_secret', '')
        logger.info(f"Client secret received: {client_secret[:20]}...")
        
        if not client_secret:
            logger.error("No client_secret in POST data")
            messages.error(request, 'Payment information is missing. Please try again.')
            return redirect(reverse('checkout'))
        
        #Include delivery_area in form data
        form_data = {
            'full_name': request.POST.get('full_name', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'phone_number': request.POST.get('phone_number', '').strip(),
            'postcode': request.POST.get('postcode', '').strip(),
            'town_or_city': request.POST.get('town_or_city', '').strip(),
            'street_address1': request.POST.get('street_address1', '').strip(),
            'street_address2': request.POST.get('street_address2', '').strip(),
            'county': request.POST.get('county', '').strip(),
            'delivery_area': request.POST.get('delivery_area', 'london'),
        }
        
        logger.info(f"Form data: {form_data}")
        order_form = OrderForm(form_data)
        
        if order_form.is_valid():
            logger.info("Order form is valid, creating order")
            try:
                with transaction.atomic():
                    # Create order
                    order = order_form.save(commit=False)
                    pid = client_secret.split('_secret')[0]
                    order.stripe_pid = pid
                    order.original_cart = json.dumps(cart) 
                    order.save()
                    logger.info(f"Order created with ID: {order.id}, Order number: {order.order_number}")
                    
                    # Create order line items
                    for item_id, item_data in cart.items():
                        try:
                            product = Product.objects.get(id=item_id)
                            if isinstance(item_data, int):
                                order_line_item = OrderItem(
                                    order=order,
                                    product=product,
                                    quantity=item_data,
                                )
                                order_line_item.save()
                                logger.info(f"Created order item: {product.name} x {item_data}")
                            
                        except Product.DoesNotExist:
                            logger.error(f"Product with ID {item_id} not found")
                            messages.error(request, (
                                f"One of the products in your cart wasn't found in our database. "
                                "Please call us for assistance!"
                            ))
                            return redirect(reverse('view_cart'))
                    
                    # Clear the cart
                    if 'cart' in request.session:
                        del request.session['cart']
                        logger.info("Cart cleared from session")
                    
                    logger.info(f"Redirecting to checkout_success with order_number: {order.order_number}")
                    return redirect(reverse('checkout_success', args=[order.order_number]))
                    
            except Exception as e:
                logger.error(f"Error processing order: {e}", exc_info=True)
                messages.error(request, 'There was an error processing your order. Please try again.')
                return redirect(reverse('checkout'))
        else:
            logger.error(f"Order form validation failed: {order_form.errors}")
            messages.error(request, 'There was an error with your form. Please check your information.')
            # Re-render the form with errors
            current_cart = cart_contents(request)
            context = {
                'order_form': order_form,
                'stripe_publishable_key': stripe_publishable_key,
                'client_secret': client_secret,
            }
            return render(request, 'checkout/checkout.html', context)
            
    else:
        # GET request
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, 'Your cart is empty. Please add items before checking out.')
            return redirect(reverse('products'))
        
        current_cart = cart_contents(request)
        total = current_cart['grand_total']
        stripe_total = round(total * 100)
        
        try:
            stripe.api_key = stripe_secret_key
            intent = stripe.PaymentIntent.create(
                amount=stripe_total,
                currency=settings.STRIPE_CURRENCY,
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            logger.info(f"Payment intent created: {intent.id}")
        except Exception as e:
            logger.error(f"Error creating payment intent: {e}")
            messages.error(request, 'There was an error setting up your payment. Please try again.')
            return redirect(reverse('view_cart'))
        
        order_form = OrderForm()
        
        if not stripe_publishable_key:
            messages.warning(request, 'Stripe public key is missing. Please contact support.')
    
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_publishable_key': stripe_publishable_key,
        'client_secret': intent.client_secret,
    }
    return render(request, template, context)

def checkout_success(request, order_number):
    """Handle successful checkouts"""
    logger.info(f"checkout_success called with order_number: {order_number}")
    try:
        order = get_object_or_404(Order, order_number=order_number)
        logger.info(f"Order found: {order.id} - {order.full_name}")
        
        # Clear any remaining cart data
        if 'cart' in request.session:
            del request.session['cart']
            logger.info("Cleared remaining cart data from session")
        
        messages.success(request, f'Order successfully processed! '
                                 f'Your order number is {order_number}. '
                                 f'A confirmation email will be sent to {order.email}.')
        
        template = 'checkout/checkout_success.html'
        context = {
            'order': order,
        }
        logger.info("Rendering checkout_success template")
        return render(request, template, context)
        
    except Exception as e:
        logger.error(f"Error in checkout success: {e}", exc_info=True)
        messages.error(request, 'There was an error displaying your order confirmation.')
        return redirect(reverse('products'))