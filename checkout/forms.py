from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    """Form for creating and updating orders."""
    
    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'phone_number', 'country', 
            'postcode', 'town_or_city', 'street_address1', 
            'street_address2', 'county'
        ]
        
    def __init__(self, *args, **kwargs):
        """Initialize the form with custom attributes."""
        super().__init__(*args, **kwargs)
        
        # Define placeholders for each field
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'country': 'Country',
            'postcode': 'Postcode',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County',
        }
        
        # Set autofocus on first field
        self.fields['full_name'].widget.attrs['autofocus'] = True
        
        # Apply styling and placeholders to all fields
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]
            
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False
            
            
            
            # Remove labels (optional - you can keep them if you want)
            # self.fields[field].label = False