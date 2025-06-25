from django.http import HttpResponse

class StripeWH_Handler:
    """Handle stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """Handle webhook events"""
        print(f"🔍 Unhandled webhook received: {event['type']}") 
        return HttpResponse(
            content = f"Webhook received: {event['type']}", status=200)
    
    def handle_payment_intent_succeeded(self, event):
        """Handle the success payment webhook from stripe"""
        return HttpResponse(
            content=f"Webhook received: {event['type']}", status=200)
    
    def handle_payment_intent_payment_failed(self, event):
        """Handle the failed payment webhook from stripe"""
        return HttpResponse(
            content=f"Webhook received: {event['type']}", status=200)
    
    def handle_payment_intent_created(self, event):
        """Handle the payment intent created webhook from stripe"""
        print(f"✅ Payment intent created: {event['id']}")
        return HttpResponse(
            content=f"Webhook received: {event['type']}", status=200)
        