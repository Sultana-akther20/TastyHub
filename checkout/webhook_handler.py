from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order, OrderItem
from products.models import Product
import json
import time
import logging
import stripe

logger = logging.getLogger(__name__)

class StripeWH_Handler:
    """Handle Stripe webhooks"""
    
    def __init__(self, request):
        self.request = request
    
    def _send_confirmation_email(self, order):
        """Send the user a confirmation email"""
        try:
            cust_email = order.email
            subject = render_to_string(
                'checkout/confirmation_emails/email_confirmation_subject.txt',
                {'order': order})
            body = render_to_string(
                'checkout/confirmation_emails/email_confirmation_body.txt',
                {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})
            
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [cust_email]
            )
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {e}")
    
    def handle_event(self, event):
        """Handle a generic/unknown/unexpected webhook event"""
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)
    
    def handle_payment_intent_succeeded(self, event):
        """Handle the payment_intent.succeeded webhook from Stripe"""
        intent = event['data']['object']
        pid = intent['id']
        bag = intent['metadata'].get('cart', '{}')
        save_info = intent['metadata'].get('save_info', False)
        
        # Get billing and shipping details
        billing_details = {
            'email': intent.get('receipt_email', ''),
            'name': '',
            'phone': '',
            'address': {
                'country': '',
                'postal_code': '',
                'city': '',
                'line1': '',
                'line2': '',
                'state': ''
            }
        }
        
        # Try to get more detailed billing info from customer or payment method
        try:
            if intent.get('customer'):
                customer = stripe.Customer.retrieve(intent['customer'])
                billing_details['email'] = customer.get('email', billing_details['email'])
                billing_details['name'] = customer.get('name', '')
                billing_details['phone'] = customer.get('phone', '')
                
                # Get address from customer if available
                if customer.get('address'):
                    billing_details['address'].update({
                        'country': customer['address'].get('country', ''),
                        'postal_code': customer['address'].get('postal_code', ''),
                        'city': customer['address'].get('city', ''),
                        'line1': customer['address'].get('line1', ''),
                        'line2': customer['address'].get('line2', ''),
                        'state': customer['address'].get('state', '')
                    })
            
            # If we have a payment method, try to get billing details from there
            if intent.get('payment_method'):
                payment_method = stripe.PaymentMethod.retrieve(intent['payment_method'])
                if payment_method.get('billing_details'):
                    pm_billing = payment_method['billing_details']
                    billing_details['email'] = pm_billing.get('email', billing_details['email'])
                    billing_details['name'] = pm_billing.get('name', billing_details['name'])
                    billing_details['phone'] = pm_billing.get('phone', billing_details['phone'])
                    
                    if pm_billing.get('address'):
                        billing_details['address'].update({
                            'country': pm_billing['address'].get('country', billing_details['address']['country']),
                            'postal_code': pm_billing['address'].get('postal_code', billing_details['address']['postal_code']),
                            'city': pm_billing['address'].get('city', billing_details['address']['city']),
                            'line1': pm_billing['address'].get('line1', billing_details['address']['line1']),
                            'line2': pm_billing['address'].get('line2', billing_details['address']['line2']),
                            'state': pm_billing['address'].get('state', billing_details['address']['state'])
                        })
        
        except Exception as e:
            logger.warning(f"Could not retrieve additional billing details: {e}")
        
        # Get shipping details
        shipping_details = intent.get('shipping')
        
        # Clean data in the shipping details
        if shipping_details and shipping_details.get('address'):
            for field, value in shipping_details['address'].items():
                if value == "":
                    shipping_details['address'][field] = None
        
        # Check if order already exists
        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                # Use appropriate details for lookup (prefer shipping, fallback to billing)
                lookup_name = shipping_details['name'] if shipping_details else billing_details['name']
                lookup_email = billing_details['email']
                lookup_phone = shipping_details['phone'] if shipping_details else billing_details['phone']
                lookup_postcode = shipping_details['address']['postal_code'] if shipping_details else billing_details['address']['postal_code']
                lookup_city = shipping_details['address']['city'] if shipping_details else billing_details['address']['city']
                lookup_line1 = shipping_details['address']['line1'] if shipping_details else billing_details['address']['line1']
                lookup_line2 = shipping_details['address']['line2'] if shipping_details else billing_details['address']['line2']
                lookup_state = shipping_details['address']['state'] if shipping_details else billing_details['address']['state']
                
                order = Order.objects.get(
                    full_name__iexact=lookup_name,
                    email__iexact=lookup_email,
                    phone_number__iexact=lookup_phone,
                    postcode__iexact=lookup_postcode,
                    town_or_city__iexact=lookup_city,
                    street_address1__iexact=lookup_line1,
                    street_address2__iexact=lookup_line2,
                    county__iexact=lookup_state,
                    original_cart=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        else:
            order = None
            try:
                # Create order using appropriate details
                # Get delivery area from metadata or default to 'london'
                delivery_area = intent['metadata'].get('delivery_area', 'london')
                
                order_data = {
                    'full_name': shipping_details['name'] if shipping_details else billing_details['name'],
                    'email': billing_details['email'],
                    'phone_number': shipping_details['phone'] if shipping_details else billing_details['phone'],
                    'delivery_area': delivery_area,
                    'postcode': shipping_details['address']['postal_code'] if shipping_details else billing_details['address']['postal_code'],
                    'town_or_city': shipping_details['address']['city'] if shipping_details else billing_details['address']['city'],
                    'street_address1': shipping_details['address']['line1'] if shipping_details else billing_details['address']['line1'],
                    'street_address2': shipping_details['address']['line2'] if shipping_details else billing_details['address']['line2'],
                    'county': shipping_details['address']['state'] if shipping_details else billing_details['address']['state'],
                    'original_cart': bag,
                    'stripe_pid': pid,
                }
                
                order = Order.objects.create(**order_data)
                
                # Create order line items
                for item_id, item_data in json.loads(bag).items():
                    try:
                        product = Product.objects.get(id=item_id)
                        if isinstance(item_data, int):
                            order_line_item = OrderItem(
                                order=order,
                                product=product,
                                quantity=item_data,
                            )
                            order_line_item.save()
                        else:
                            # Handle size variations if needed
                            for size, quantity in item_data['items_by_size'].items():
                                order_line_item = OrderItem(
                                    order=order,
                                    product=product,
                                    quantity=quantity,
                                    product_size=size,
                                )
                                order_line_item.save()
                    except Product.DoesNotExist:
                        logger.error(f"Product with id {item_id} not found")
                        if order:
                            order.delete()
                        return HttpResponse(
                            content=f'Webhook received: {event["type"]} | ERROR: Product not found',
                            status=500)
                
                # IMPORTANT: After creating all order items, update the order
                # This will recalculate delivery_cost, order_total, and grand_total
                order.update_total()
                            
            except Exception as e:
                logger.error(f"Error creating order in webhook: {e}")
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        
        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)
    
    def handle_payment_intent_payment_failed(self, event):
        """Handle the payment_intent.payment_failed webhook from Stripe"""
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)