from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product listing and detail views
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Category views
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    
    # Featured and special views
    path('featured/', views.FeaturedProductsView.as_view(), name='featured_products'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    
    # API endpoints (optional)
    path('api/products/', views.ProductAPIView.as_view(), name='product_api'),
    path('api/categories/', views.CategoryAPIView.as_view(), name='category_api'),
    
    # AJAX views for dynamic loading
    path('ajax/products/', views.ProductAjaxView.as_view(), name='product_ajax'),
    path('ajax/category/<int:category_id>/', views.CategoryProductsAjaxView.as_view(), name='category_products_ajax'),
]