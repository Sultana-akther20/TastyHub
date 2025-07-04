from .models import ProductReview, Contact 
from django import forms
from django.core.validators import validate_email

class ProductReviewForm(forms.ModelForm):
    """Form for customer reviews"""
    
    class Meta:
        model = ProductReview
        fields = ['customer_name', 'customer_email', 'rating', 'comment']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
                'required': True
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this dish...',
                'required': True
            }),
        }
        labels = {
            'customer_name': 'Your Name',
            'customer_email': 'Email Address',
            'rating': 'Rating',
            'comment': 'Your Review',
        }
    
    def clean_customer_email(self):
        email = self.cleaned_data.get('customer_email')
        if email:
            validate_email(email)
        return email
    
    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if comment and len(comment.strip()) < 10:
            raise forms.ValidationError('Please provide a more detailed review (at least 10 characters).')
        return comment

class ContactForm(forms.Form):
    """Form for contact/complaints"""
    
    INQUIRY_TYPES = [
        ('food_quality', 'Food Quality Issue'),
        ('delivery', 'Delivery Problem'),
        ('service', 'Service Complaint'),
        ('billing', 'Billing Issue'),
        ('suggestion', 'Suggestion'),
        ('compliment', 'Compliment'),
        ('other', 'Other'),
    ]
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name',
            'required': True
        }),
        label='Full Name'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'required': True
        }),
        label='Email Address'
    )
    
    phone = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+44(0)'
        }),
        label='Phone Number (Optional)'
    )
    
    inquiry_type = forms.ChoiceField(
        choices=INQUIRY_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='Type of Inquiry'
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Brief subject',
            'required': True
        }),
        label='Subject'
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Please provide details about your inquiry...',
            'required': True
        }),
        label='Message'
    )
    
    # Order reference for complaints
    order_reference = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Order #12'
        }),
        label='Order Ref: (Optional)'
    )
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if message and len(message.strip()) < 20:
            raise forms.ValidationError('Please provide more details (at least 20 characters).')
        return message
    
    def save(self):
        """Save contact form data"""
        return self.cleaned_data

# save contact forms to database
class ContactModel(forms.ModelForm):
    """Alternative form that saves to a Contact model"""
    
    class Meta:
        model = None  
        fields = ['name', 'email', 'phone', 'inquiry_type', 'subject', 'message', 'order_reference']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+44(0)'}),
            'inquiry_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Your message...'}),
            'order_reference': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Order #12'}),
        }

