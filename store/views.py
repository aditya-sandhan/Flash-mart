from django.shortcuts import render, redirect
from .models import Product, Shopkeeper
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

def customer_signup(request):
    return render(request, 'customer_signup.html')


def shopkeeper_signup(request):
    if request.method == 'POST':
       
        name = request.POST.get('name')
        email = request.POST.get('email')
        shop_name = request.POST.get('shop_name')
        address = request.POST.get('address')
        password = request.POST.get('password')

        # database save
        Shopkeeper.objects.create(
            full_name=name,
            email=email,
            shop_name=shop_name,
            address=address,
            password=password
        )

       
        return redirect('home')

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
    """
    Secures the dashboard and displays shop-specific data. [cite: 2025-12-26]
    """
    # Security Check: Only allow logged-in shopkeepers [cite: 2025-12-26]
    if request.session.get('user_role') != 'shopkeeper':
        return redirect('login')

    # Fetch shop data using session ID [cite: 2025-12-26]
    shop = Shopkeeper.objects.get(id=request.session['user_id'])
    return render(request, 'shop_dashboard.html', {'shop': shop})



def add_product(request):
    """
    Handles secure product creation by the logged-in shopkeeper. [cite: 2025-12-26]
    """
    # 1. Access security: Only shopkeepers can add products [cite: 2025-12-26]
    if request.session.get('user_role') != 'shopkeeper':
        return redirect('login')

    if request.method == 'POST':
        # 2. Extract data from form [cite: 2025-12-26]
        p_name = request.POST.get('name')
        mrp = request.POST.get('mrp')
        current_p = request.POST.get('start_price')
        exp_date = request.POST.get('expiry')

        # 3. Link product to the specific shopkeeper [cite: 2025-12-26]
        owner = Shopkeeper.objects.get(id=request.session['user_id'])

        # 4. Save to Database [cite: 2025-12-26]
        Product.objects.create(
            name=p_name,
            original_price=mrp,
            current_price=current_p,
            expiry_date=exp_date,
            # (Note: Ensure your Product model has a Foreignkey to Shopkeeper)
        )
        
        return redirect('shop_dashboard')

    return render(request, 'add_product_form.html')