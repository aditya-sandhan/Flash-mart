from django.urls import path
from . import views

urlpatterns = [
   
    path('home/', views.home, name='home'),
    path('select-role/', views.select_role, name='select_role'),
]