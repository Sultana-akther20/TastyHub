# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect, reverse
#from django.views.generic import ListView, DetailView
from django.db.models import Q
#from django.http import JsonResponse
#from django.core.paginator import Paginator
from django.contrib import messages
from .models import Product, Category, ProductImage, ProductReview

def all_products(request):
    """Display all products including filtering and searching"""
    products = Product.objects.all()
    query = None
    current_categories = None  # Initialize this variable properly
    
    if request.GET:
        if 'category' in request.GET:
            category_names = request.GET['category'].split(',')
            # Handle URL encoding (spaces become %20)
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
    
    # Context should always be defined, regardless of whether there's a search
    context = {
        'products': products,
        'categories': Category.objects.filter(is_active=True, parent=None).order_by('order'),
        'current_categories': current_categories,  # This will be None if no category filter
        'search_term': query,
    }
    
    return render(request, 'products/products.html', context)

def details(request, product_id):
    """Display individual product including filtering and searching"""
    product = get_object_or_404(Product, pk=product_id)
    context = {
        'product': product,
    }
    return render(request, 'products/details.html', context)