from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    """Form for creating and updating orders."""
    
    class Meta:
        model = Order
        fields = [
            'full_name', 'email', 'street_address1', 
            'street_address2', 'postcode', 'town_or_city', 
            'phone_number', 'county', 'delivery_area'
        ]
        
    def __init__(self, *args, **kwargs):
        """Initialize the form with custom attributes."""
        super().__init__(*args, **kwargs)
        
        # Make delivery_area field more descriptive
        self.fields['delivery_area'].widget.attrs['class'] = 'stripe-style-input form-select'
        self.fields['delivery_area'].empty_label = "Select delivery area"
        
        # Define placeholders for each field
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'town_or_city': 'Town or City',
            'postcode': 'Postcode',
            'phone_number': 'Phone Number',
            'county': 'County',
            'delivery_area': 'Delivery Area',
        }
        
        self.fields['full_name'].widget.attrs['autofocus'] = True
        
        # Apply styling and placeholders to all fields
        for field in self.fields:
            if field == 'delivery_area':
                # Skip placeholder for choice field
                continue
                
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = placeholders[field]
            
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].label = False