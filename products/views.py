from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.db.models import Q, Avg
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Product, Category, ProductImage, ProductReview, Contact
from .forms import ProductReviewForm, ContactForm

def all_products(request):
    """Display all products including filtering and searching"""
    products = Product.objects.all()
    query = None
    current_categories = None
    
    if request.GET:
        if 'category' in request.GET:
            category_names = request.GET['category'].split(',')
            category_names = [name.strip().replace('%20', ' ') for name in category_names]
            products = products.filter(category__name__in=category_names)
            current_categories = Category.objects.filter(name__in=category_names)
            
        if 'q' in request.GET:
            query = request.GET.get('q')
            if not query:
                messages.error(request, "Please enter a search term.")
                return redirect(reverse('products'))
            
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)
    
    # Add pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': Category.objects.filter(is_active=True, parent=None).order_by('order'),
        'current_categories': current_categories,
        'search_term': query,
    }
    
    return render(request, 'products/products.html', context)

def details(request, product_id):
    """Display individual product with reviews and review form"""
    product = get_object_or_404(Product, pk=product_id)
    
    # Get approved reviews
    reviews = ProductReview.objects.filter(
        product=product, 
        is_approved=True
    ).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)
    
    # Get review form
    review_form = ProductReviewForm()
    
    # Handle AJAX review submission
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        review_form = ProductReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your review! It will be published after approval.'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': review_form.errors
            })
    
    # Get related products (same category)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': reviews.count(),
        'review_form': review_form,
        'related_products': related_products,
    }
    
    return render(request, 'products/details.html', context)

@require_POST
def add_review(request, product_id):
    """Handle review submission via regular form"""
    product = get_object_or_404(Product, pk=product_id)
    form = ProductReviewForm(request.POST)
    
    if form.is_valid():
        # Check if user already reviewed this product
        existing_review = ProductReview.objects.filter(
            product=product,
            customer_email=form.cleaned_data['customer_email']
        ).first()
        
        if existing_review:
            messages.warning(request, 'You have already reviewed this product.')
        else:
            review = form.save(commit=False)
            review.product = product
            review.save()
            messages.success(request, 'Thank you for your review! It will be published after approval.')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')
    
    return redirect('details', product_id=product_id)




def contact_view(request):
    """Handle contact form and complaints"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = Contact.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                inquiry_type=form.cleaned_data['inquiry_type'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                order_reference=form.cleaned_data['order_reference']
            )
            
            # Send email notification to admin
            try:
                subject = f'New Contact Form Submission: {contact.subject}'
                message = f"""
                Name: {contact.name}
                Email: {contact.email}
                Type: {contact.get_inquiry_type_display()}
                
                Message:
                {contact.message}
                
                Submitted at: {contact.created_at}
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL], 
                    fail_silently=False,
                )
                
                # Send confirmation email to customer
                customer_subject = 'Thank you for contacting TastyHub'
                customer_message = f"""
                Dear {contact.name},
                
                Thank you for contacting TastyHub. We have received your message and will get back to you within 24 hours.
                
                Your inquiry details:
                Subject: {contact.subject}
                Type: {contact.get_inquiry_type_display()}
                
                Best regards,
                TastyHub Team
                """
                
                send_mail(
                    customer_subject,
                    customer_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [contact.email],
                    fail_silently=True,
                )
                
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return redirect('contact_success')
                
            except Exception as e:
                messages.error(request, f'There was an error sending your message: {str(e)}')
                print(f"Email error: {e}")  # For debugging
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'products/contact.html', context)

def contact_success(request):
    """Display contact success page"""
    return render(request, 'products/contact_success.html')

def reviews_list(request, product_id):
    """Display all reviews for a product"""
    product = get_object_or_404(Product, pk=product_id)
    reviews = ProductReview.objects.filter(
        product=product,
        is_approved=True
    ).order_by('-created_at')
    
    # Pagination for reviews
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'product': product,
        'reviews': page_obj,
    }
    
    return render(request, 'products/reviews_list.html', context)