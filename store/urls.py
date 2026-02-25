from django.urls import path
from . import views

urlpatterns = [
   
    path('home/', views.home, name='home'),
    path('select-role/', views.select_role, name='select_role'),
    # Role selection ke niche ye daal:
    path('signup/customer/', views.customer_signup, name='customer_signup'),
    path('signup/shopkeeper/', views.shopkeeper_signup, name='shopkeeper_signup'),
    path('signup/franchise/', views.franchise_signup, name='franchise_signup'),
]