# Short imports including helper and Category
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Shopkeeper, Category
from django.utils import timezone # For handling dates
# Create your views here.

def home(request):
    products = Product.objects.all().order_by('-created_at')
    context = {
        'products': products
    }
    
    return render(request, 'home.html', context)

def select_role(request):
    return render(request, 'role_selection.html')



def shopkeeper_signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        shop_name = request.POST.get('shop_name')
        address = request.POST.get('address')
        password = request.POST.get('password')

        # 1. Save to database and capture the object
        new_shop = Shopkeeper.objects.create(
            full_name=name, email=email, shop_name=shop_name,
            address=address, password=password
        )

        # 2. AUTO-LOGIN: Set the session variables immediately
        request.session['user_role'] = 'shopkeeper'
        request.session['user_id'] = new_shop.id

        # 3. Redirect to their new dashboard
        return redirect('shop_dashboard')

    return render(request, 'shopkeeper_signup.html')



def customer_signup(request):
    if request.method == 'POST':
        # Customer basic info
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(f"New Customer: {name} ({email})")
        return redirect('home')

    return render(request, 'customer_signup.html')


def franchise_signup(request):
    return render(request, 'franchise_signup.html')

def login_view(request):
    """
    Handles unified authentication for both Customers and Shopkeepers.
    Redirects users to their respective dashboards based on role.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if user exists in Shopkeeper records
        shopkeeper = Shopkeeper.objects.filter(email=email, password=password).first()
        if shopkeeper:
            # Store shopkeeper identity in session
            request.session['user_role'] = 'shopkeeper'
            request.session['user_id'] = shopkeeper.id
            return redirect('shop_dashboard') # We will create this URL next

        # Check if user exists in Customer records (Placeholder for now)
        # customer = Customer.objects.filter(email=email, password=password).first()
        # if customer:
        #     request.session['user_role'] = 'customer'
        #     return redirect('home')

        # Handle invalid credentials
        return render(request, 'login.html', {'error': 'Invalid Email or Password'})

    return render(request, 'login.html')

def shop_dashboard(request):
    """Secured dashboard with Product fetching"""
    if request.session.get('user_role') != 'shopkeeper':
        return redirect('login')

    shop = Shopkeeper.objects.get(id=request.session['user_id'])
    # FETCH PRODUCTS FOR THIS SHOPKEEPER
    products = Product.objects.filter(shopkeeper=shop).order_by('expiry_time')
    
    # PASS PRODUCTS TO TEMPLATE
    return render(request, 'shop_dashboard.html', {'shop': shop, 'products': products})


def logout_view(request):
    """Clears the user's session and redirects to home."""
    # Remove all session data for the current session
    request.session.flush()
    return redirect('home')

def products_list(request):
    """Show all products (used by 'View All Deals' links)."""
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'products': products})


def product_detail(request, product_id):
    """Basic product detail view (creates a simple product page)."""
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_detail.html', {'product': product})


def add_product(request):
    """Synchronized Save Logic with Dynamic Categories"""
    if request.session.get('user_role') != 'shopkeeper':
        return redirect('login')

    if request.method == 'POST':
        owner = Shopkeeper.objects.get(id=request.session['user_id'])
        
        # 1. Jo category form se aayi hai, uski ID pakdo
        cat_id = request.POST.get('category')
        selected_category = Category.objects.get(id=cat_id) if cat_id else None

        # 2. Product save karte waqt category bhi attach kar do
        Product.objects.create(
            shopkeeper=owner,
            category=selected_category, # <--- THE FIX
            name=request.POST.get('name'),
            original_price=request.POST.get('mrp'),
            expiry_time=request.POST.get('expiry')
        )
        return redirect('shop_dashboard')

    # GET REQUEST: Database se saari categories uthao aur form ko bhejo
    categories = Category.objects.all()
    return render(request, 'add_product_form.html', {'categories': categories})