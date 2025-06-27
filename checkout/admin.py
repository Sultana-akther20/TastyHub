from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.
class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem model."""
    model = OrderItem
    readonly_fields = ('lineitem_total',)
    
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model."""
    inlines = (OrderItemInline,)
    readonly_fields = ('order_number', 'date', 'delivery_cost', 'order_total', 'grand_total', 'original_cart', 'stripe_pid')
    fields = ('order_number', 'full_name', 'email', 'phone_number', 'country', 
              'postcode', 'town_or_city', 'street_address1', 'street_address2', 
              'county', 'date', 'delivery_cost', 'order_total', 'grand_total', 'original_cart', 'stripe_pid')
    list_display = ('order_number', 'full_name', 'date', 'order_total', 'delivery_cost', 'grand_total')
    ordering = ('-date',)

admin.site.register(Order, OrderAdmin)