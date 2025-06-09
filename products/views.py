

# Create your views here.



from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q, Prefetch
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views import View
from .models import Product, Category, ProductImage, ProductReview


class ProductListView(ListView):
    """Display all available products"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True).select_related('category').prefetch_related('additional_images')
        
        # Filter by category if provided
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by search query
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(ingredients__icontains=search_query)
            )
        
        # Filter by price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Ordering
        order_by = self.request.GET.get('order', '-is_featured')
        if order_by in ['price', '-price', 'name', '-name', 'preparation_time', '-preparation_time']:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by('-is_featured', 'category__order', 'name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent=None).order_by('order')
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class ProductDetailView(DetailView):
    """Display individual product details"""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(is_available=True).select_related('category').prefetch_related(
            'additional_images',
            'reviews__approved=True',
            'nutrition'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Related products from same category
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id).select_related('category')[:4]
        
        # Approved reviews
        context['reviews'] = product.reviews.filter(is_approved=True).order_by('-created_at')
        context['review_count'] = context['reviews'].count()
        
        # Average rating
        if context['review_count'] > 0:
            total_rating = sum([review.rating for review in context['reviews']])
            context['average_rating'] = round(total_rating / context['review_count'], 1)
        else:
            context['average_rating'] = 0
        
        return context


class CategoryListView(ListView):
    """Display all categories"""
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True, parent=None).prefetch_related('subcategories').order_by('order')


class CategoryDetailView(DetailView):
    """Display products in a specific category"""
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).prefetch_related('products')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        
        # Get products in this category and subcategories
        category_ids = [category.id] + [child.id for child in category.get_all_children]
        products = Product.objects.filter(
            category_id__in=category_ids,
            is_available=True
        ).select_related('category').order_by('-is_featured', 'name')
        
        # Paginate products
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['products'] = page_obj
        context['subcategories'] = category.subcategories.filter(is_active=True).order_by('order')
        
        return context


class FeaturedProductsView(ListView):
    """Display featured products"""
    model = Product
    template_name = 'products/featured_products.html'
    context_object_name = 'products'
    paginate_by = 8
    
    def get_queryset(self):
        return Product.objects.filter(
            is_available=True,
            is_featured=True
        ).select_related('category').order_by('-created_at')


class ProductSearchView(ListView):
    """Handle product search"""
    model = Product
    template_name = 'products/search_results.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(ingredients__icontains=query) |
                Q(category__name__icontains=query),
                is_available=True
            ).select_related('category').distinct()
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


# API Views for AJAX requests
class ProductAPIView(View):
    """API endpoint for products"""
    def get(self, request):
        products = Product.objects.filter(is_available=True).select_related('category')
        
        # Filter by category if provided
        category_id = request.GET.get('category_id')
        if category_id:
            products = products.filter(category_id=category_id)
        
        # Filter by featured if provided
        featured = request.GET.get('featured')
        if featured == 'true':
            products = products.filter(is_featured=True)
        
        # Limit results
        limit = int(request.GET.get('limit', 10))
        products = products[:limit]
        
        data = []
        for product in products:
            data.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': str(product.price),
                'category': product.category.name,
                'image': product.image.url if product.image else None,
                'is_featured': product.is_featured,
                'preparation_time': product.preparation_time,
                'calories': product.calories,
            })
        
        return JsonResponse({'products': data})


class CategoryAPIView(View):
    """API endpoint for categories"""
    def get(self, request):
        categories = Category.objects.filter(is_active=True).order_by('order')
        
        # Filter by parent if provided
        parent_id = request.GET.get('parent_id')
        if parent_id:
            categories = categories.filter(parent_id=parent_id)
        elif parent_id is None:
            categories = categories.filter(parent=None)
        
        data = []
        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'slug': category.slug,
                'parent_id': category.parent_id,
                'product_count': category.products.filter(is_available=True).count(),
            })
        
        return JsonResponse({'categories': data})


class ProductAjaxView(View):
    """AJAX view for loading products dynamically"""
    def get(self, request):
        page = int(request.GET.get('page', 1))
        category_id = request.GET.get('category_id')
        search_query = request.GET.get('q', '')
        
        products = Product.objects.filter(is_available=True).select_related('category')
        
        if category_id:
            products = products.filter(category_id=category_id)
        
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        paginator = Paginator(products, 12)
        page_obj = paginator.get_page(page)
        
        data = {
            'products': [
                {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description[:100] + '...' if len(product.description) > 100 else product.description,
                    'price': str(product.price),
                    'category': product.category.name,
                    'image': product.image.url if product.image else None,
                    'is_featured': product.is_featured,
                    'slug': product.slug,
                }
                for product in page_obj
            ],
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        }
        
        return JsonResponse(data)


class CategoryProductsAjaxView(View):
    """AJAX view for loading products by category"""
    def get(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id, is_active=True)
            products = Product.objects.filter(
                category=category,
                is_available=True
            ).select_related('category')[:8]
            
            data = {
                'category': {
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                },
                'products': [
                    {
                        'id': product.id,
                        'name': product.name,
                        'description': product.description[:100] + '...' if len(product.description) > 100 else product.description,
                        'price': str(product.price),
                        'image': product.image.url if product.image else None,
                        'slug': product.slug,
                    }
                    for product in products
                ]
            }
            
            return JsonResponse(data)
        
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)