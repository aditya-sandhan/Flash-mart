from django.shortcuts import render
from .models import Product
# Create your views here.

def home(request):
    products = Product.objects.all().order_by('-created_at')
    context = {
        'products': products
    }
    
    return render(request, 'home.html', context)

def select_role(request):
    return render(request, 'role_selection.html')