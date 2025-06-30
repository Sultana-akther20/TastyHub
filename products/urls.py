from django.urls import path
from . import views


urlpatterns = [
    path('', views.all_products, name='products'),
    path('<int:product_id>/', views.details, name='details'),
     # Review URLs
    path('<int:product_id>/review/', views.add_review, name='add_review'),
    path('<int:product_id>/reviews/', views.reviews_list, name='reviews_list'),
    
    # Contact URLs
    path('contact/', views.contact_view, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
]