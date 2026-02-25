# Short imports including helper and Category
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Shopkeeper, Category,Order
from .models import Customer 
from django.utils import timezone # For handling dates
# Create your views here.

# Isko update kar
def home(request):
    now = timezone.now()
    
    # 1. Product Expire nahi hona chahiye (expiry_time > now)
    # 2. Product kisi ne Grab nahi kiya hona chahiye 
    
    products = Product.objects.filter(
        expiry_time__gt=now,
        orders__isnull=True  # Sirf wo products jo abhi tak sold nahi hue
    ).order_by('expiry_time')
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'home.html', context)

def select_role(request):
    """Simple view to let users choose between Shopkeeper or Customer"""
    return render(request, 'select_role.html')

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
    """Creates a customer with error handling and auto-logs them in"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        #Check if email already exists before saving!
        if Customer.objects.filter(email=email).exists():
            return render(request, 'customer_signup.html', {
                'error': 'This email is already registered. Please login instead.'
            })
        
        # Save to database
        new_customer = Customer.objects.create(
            full_name=name, email=email, password=password
        )
        
        # Auto-login session creation
        request.session['user_role'] = 'customer'
        request.session['user_id'] = new_customer.id
        
       
        return redirect('customer_dashboard') 
        
    return render(request, 'customer_signup.html')

def franchise_signup(request):
    return render(request, 'franchise_signup.html')

def login_view(request):
    """Handles authentication for both Customers and Shopkeepers"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 1. Check Shopkeeper first
        shopkeeper = Shopkeeper.objects.filter(email=email, password=password).first()
        if shopkeeper:
            request.session['user_role'] = 'shopkeeper'
            request.session['user_id'] = shopkeeper.id
            return redirect('shop_dashboard')

        # 2. Check Customer
        customer = Customer.objects.filter(email=email, password=password).first()
        if customer:
            request.session['user_role'] = 'customer'
            request.session['user_id'] = customer.id
            # 🚨 REDIRECT FIX: Send to dashboard, not home
            return redirect('customer_dashboard')

        return render(request, 'login.html', {'error': 'Invalid Email or Password'})

    return render(request, 'login.html')

def shop_dashboard(request):
    """Shows the shopkeeper their products and active customer orders"""
    if request.session.get('user_role') != 'shopkeeper':
        return redirect('login')

    shop = Shopkeeper.objects.get(id=request.session['user_id'])
    
    # 1. Fetch their active inventory
    products = Product.objects.filter(shopkeeper=shop).order_by('expiry_time')
    
    # 2. THE NEW LOGIC: Fetch orders related to THIS shop's products
    orders = Order.objects.filter(product__shopkeeper=shop).order_by('-order_time')
    
    # 3. Calculate total money made from locked orders
    total_revenue = sum(order.locked_price for order in orders)

    context = {
        'shop': shop,
        'products': products,
        'orders': orders,
        'total_revenue': round(total_revenue, 2)
    }
    return render(request, 'shop_dashboard.html', context)




def customer_dashboard(request):
    """Secures and displays customer-specific data & reservations"""
    if request.session.get('user_role') != 'customer':
        return redirect('login')

    customer = Customer.objects.get(id=request.session['user_id'])
    
    # 1. Fetch all orders for this specific customer (Newest first)
    orders = Order.objects.filter(customer=customer).order_by('-order_time')
    
    # 2. Calculate the  Total Savings!
    total_savings = sum((order.product.original_price - order.locked_price) for order in orders)

    context = {
        'customer': customer,
        'orders': orders,
        'total_orders': orders.count(),
        'total_savings': round(total_savings, 2)
    }
    
    return render(request, 'customer_dashboard.html', context)

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




def category_list(request):
    """Displays all available categories with an attractive UI"""
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def category_products(request, cat_id):
    """Filters products by the selected category"""
    category = get_object_or_404(Category, id=cat_id)
    # Sirf us specific category ke products uthao, expiry ke hisaab se sort karke
    products = Product.objects.filter(category=category).order_by('expiry_time')
    return render(request, 'category_products.html', {'category': category, 'products': products})


def grab_product(request, product_id):
    """Locks the exact current price and reserves the item for the customer"""
    
    # 1. Sirf logged-in customers kharid sakte hain
    if request.session.get('user_role') != 'customer':
        return redirect('login')
        
    customer = Customer.objects.get(id=request.session['user_id'])
    product = get_object_or_404(Product, id=product_id)
    
    # 2. Safety Check: Agar product expire ho gaya hai toh reject kar do
    if timezone.now() >= product.expiry_time:
        return redirect('home') # (Future idea: Yahan error message dikha sakte hain)
        
    # 3. THE MAGIC: Lock the exact price at this specific second
    locked_price = product.current_price
    
    # 4. Save the order to database
    Order.objects.create(
        customer=customer,
        product=product,
        locked_price=locked_price,
        status='Reserved'
    )
    
    # 5. Redirect user to their dashboard to see their reservation
    return redirect('customer_dashboard')


def mark_picked_up(request, order_id):
    """Changes the order status when the customer collects the item"""
    if request.session.get('user_role') != 'shopkeeper':
        return redirect('login')
        
    order = get_object_or_404(Order, id=order_id)
    
    # 🚨 Security Check: Ensure the shopkeeper owns this product
    if order.product.shopkeeper.id == request.session['user_id']:
        order.status = 'Picked Up'
        order.save()
        
    return redirect('shop_dashboard')