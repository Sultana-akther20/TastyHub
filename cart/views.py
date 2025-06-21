from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from products.models import Product
from django.http import JsonResponse
import json

def view_cart(request):
    """Display the shopping cart"""
    # Debug: Print cart contents
    cart = request.session.get('cart', {})
    print(f"Cart contents: {cart}")
    return render(request, 'cart/cart.html')

def add_to_cart(request, product_id):
    """Add a product to the shopping cart"""
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url')
    cart = request.session.get('cart', {})
    
    # Convert product_id to string for session storage
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += quantity
        messages.success(request, f'Updated {product.name} quantity to {cart[product_id_str]}')
    else:
        cart[product_id_str] = quantity
        messages.success(request, f'Added {product.name} to your cart')
    
    request.session['cart'] = cart
    print(f"Cart after adding: {cart}")  # Debug
    return redirect(redirect_url)

def adjust_bag(request, product_id):
    """Adjust the quantity of a product in the cart"""
    if request.method != 'POST':
        return redirect('view_cart')
        
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity', 0))
    cart = request.session.get('cart', {})
    
    # Convert product_id to string for session storage
    product_id_str = str(product_id)
    
    print(f"Adjusting product {product_id_str} to quantity {quantity}")  # Debug
    
    if quantity > 0:
        cart[product_id_str] = quantity
        messages.success(request, f'Updated {product.name} quantity to {cart[product_id_str]}')
    else:
        if product_id_str in cart:
            cart.pop(product_id_str)
            messages.success(request, f'Removed {product.name} from your cart')
    
    request.session['cart'] = cart
    print(f"Cart after adjustment: {cart}")  # Debug
    return redirect(reverse('view_cart'))

def update_cart(request, product_id):
    """Update the quantity of a product in the cart"""
    product = get_object_or_404(Product, pk=product_id)
    quantity = int(request.POST.get('quantity'))
    cart = request.session.get('cart', {})
    
    # Convert product_id to string for session storage
    product_id_str = str(product_id)
    
    if quantity > 0:
        cart[product_id_str] = quantity
        messages.success(request, f'Updated {product.name} quantity to {cart[product_id_str]}')
    else:
        if product_id_str in cart:
            cart.pop(product_id_str)
            messages.success(request, f'Removed {product.name} from your cart')
    
    request.session['cart'] = cart
    return redirect('view_cart')

def remove_from_cart(request, product_id):
    """Remove a product from the cart via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
        
    try:
        product = get_object_or_404(Product, pk=product_id)
        cart = request.session.get('cart', {})
        
        # Convert product_id to string for session storage
        product_id_str = str(product_id)
        
        print(f"Removing product {product_id_str} from cart")  # Debug
        
        if product_id_str in cart:
            current_quantity = cart[product_id_str]
            
            # Check if this is a decrement action or complete removal
            action = request.POST.get('action', 'remove_all')
            
            if action == 'decrement':
                if current_quantity > 1:
                    # Reduce quantity by 1
                    cart[product_id_str] = current_quantity - 1
                    messages.success(request, f'Reduced {product.name} quantity to {cart[product_id_str]}')
                else:
                    # Remove completely if quantity is 1
                    cart.pop(product_id_str)
                    messages.success(request, f'Removed {product.name} from your cart')
            else:
                # Remove completely
                cart.pop(product_id_str)
                messages.success(request, f'Removed {product.name} from your cart')
            
            request.session['cart'] = cart
            print(f"Cart after removal: {cart}")  # Debug
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'message': 'Item not found'})
    except Exception as e:
        print(f"Error removing item: {str(e)}")  # Debug
        return JsonResponse({'success': False, 'message': str(e)})