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

        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'postcode': forms.TextInput(attrs={'placeholder': 'Postcode'}),
            'town_or_city': forms.TextInput(attrs={'placeholder': 'Town or City'}),
            'street_address1': forms.TextInput(attrs={'placeholder': 'Street Address 1'}),
            'street_address2': forms.TextInput(attrs={'placeholder': 'Street Address 2'}),
            'county': forms.TextInput(attrs={'placeholder': 'County'}),
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{widgets[field]} *'
            else:
                placeholder = widgets[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
                self.fields[field].widget.attrs['class'] = 'stripe-style-input'
                self.fields[field].label = False