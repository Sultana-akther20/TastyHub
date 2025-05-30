from django.shortcuts import render

# Create your views here.
def index(request):
    """
    Render the index page of the hub.
    """
    return render(request, 'hub/index.html')