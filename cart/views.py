from django.shortcuts import render

# Create your views here.
def view_cart(request):
    """Display the shopping cart"""
    #cart = request.session.get('cart', {})
    #total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    
    #context = {
        #'cart': cart,
        #'total_price': total_price,
    #}
    
    return render(request, 'cart/cart.html')