from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from checkout.webhook_handler import StripeWH_Handler
import stripe
import logging

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Setup
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # Check if signature header exists
    if not sig_header:
        logger.error("Missing Stripe signature header")
        return HttpResponse(content="Missing signature header", status=400)
    
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(content="Invalid payload", status=400)
    
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(content="Invalid signature", status=400)
    
    except Exception as e:
        # Other errors
        logger.error(f"Webhook error: {e}")
        return HttpResponse(content="Webhook error", status=400)
    
    # Set up a webhook handler
    handler = StripeWH_Handler(request)
    
    # Map webhook events to relevant handler functions
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }
    
    # Get the webhook type from Stripe
    event_type = event['type']
    
    # If there's a handler for it, get it from the event map
    # Use the generic one by default
    event_handler = event_map.get(event_type, handler.handle_event)
    
    # Call the event handler with the event
    response = event_handler(event)
    return response