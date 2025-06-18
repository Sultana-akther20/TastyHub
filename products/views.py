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
    if request.GET:
        if 'q' in request.GET:
            query = request.GET.get('q')
        if not query:
            messages.error(request, "Please enter a search term.")
            return redirect(reverse('products'))
        
        queries = Q(name__icontains=query) | Q(description__icontains=query)
        products = products.filter(queries)

        context = {
        'products': products,
        'categories': Category.objects.filter(is_active=True, parent=None).order_by('order'),
        'current_category': request.GET.get('category', ''),
        #'search_query': request.GET.get('q', ''),
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



