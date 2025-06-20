from django.shortcuts import render,redirect

# Create your views here.
def view_cart(request):
    """Display the shopping cart"""
   
    return render(request, 'cart/cart.html')

def add_to_cart(request, product_id):
    """Add a product to the shopping cart"""
    quantity=int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url')
    cart= request.session.get('cart', {})

    if product_id in list(cart.keys()):
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity

    request.session['cart'] = cart
    # Logic to add the product to the cart
    # This is a placeholder; actual implementation will depend on your cart model
    return redirect(redirect_url)

def add_to_cart(request, product_id):
    """add a quantity for the products"""
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    cart = request.session.get('cart', {})

    if product_id in list(cart.keys()):
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity

    request.session['cart'] = cart
    print(request.session['cart'])
    return redirect(redirect_url)