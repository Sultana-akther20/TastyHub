# Create your views here.
from django.shortcuts import render, get_object_or_404
#from django.views.generic import ListView, DetailView
#from django.db.models import Q, Prefetch, Avg
#from django.http import JsonResponse
#from django.core.paginator import Paginator
#from django.views import View
from .models import Product, Category, ProductImage, ProductReview

def all_products(request):
    """Display all products including filtering and searching"""

    products = Product.objects.all()
    context = {
        'products': products,
        'categories': Category.objects.filter(is_active=True, parent=None).order_by('order'),
        'current_category': request.GET.get('category', ''),
        'search_query': request.GET.get('q', ''),
    }
    return render(request, 'products/products.html', context)


def details(request, product_id):
    """Display individual product including filtering and searching"""

    product = get_object_or_404(Product, pk=product_id)
    context = {
        'product': product,
       
    }
    return render(request, 'products/details.html', context)



