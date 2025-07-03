import uuid
from django.db import models
from django.conf import settings
from django.db.models import Sum
from products.models import Product

class Order(models.Model):
    DELIVERY_AREAS = [
        ('london', 'London'),
    ]
    
    delivery_area = models.CharField(
        max_length=50,
        choices=DELIVERY_AREAS,
        default='london'
    )
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0.00)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.00)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.00)
    original_cart = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default='')

    def _generate_order_number(self):
        """Generate a random unique order number using UUID."""
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """Override the save method to set the order number if not already set."""
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def update_total(self):
        """Update grand total each time an item is added to the order."""
        # Calculate order total from line items using the correct related_name 'items'
        self.order_total = self.items.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        
        # Calculate delivery cost based on delivery area (not free delivery threshold)
        if self.delivery_area == 'london':
            # Use your actual London delivery cost here
            self.delivery_cost = getattr(settings, 'LONDON_DELIVERY_COST', 5.00)
        else:
            # Default delivery cost for other areas
            self.delivery_cost = 0.00
        
        # Calculate grand total
        self.grand_total = self.order_total + self.delivery_cost
        
        # Save the order
        self.save()

    def __str__(self):
        """Return a string representation of the order."""
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    def save(self, *args, **kwargs):
        """Override the save method to set the lineitem_total and update the order total."""
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        # Update the order total after saving this item
        self.order.update_total()

    def __str__(self):
        """Return a string representation of the order item."""
        return f'Order {self.order.order_number} Item {self.id}'