from django.urls import path
from . import views

urlpatterns = [
   
    path('', views.home, name='home'),
    path('select-role/', views.select_role, name='select_role'),
    path('products/', views.products_list, name='products_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    # Role selection ke niche ye daal:
    path('signup/customer/', views.customer_signup, name='customer_signup'),
    path('signup/shopkeeper/', views.shopkeeper_signup, name='shopkeeper_signup'),
    path('signup/franchise/', views.franchise_signup, name='franchise_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/shop/', views.shop_dashboard, name='shop_dashboard'), # Placeholder
    path('dashboard/shop/add-product/', views.add_product, name='add_product'),
]