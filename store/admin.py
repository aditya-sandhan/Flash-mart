from django.contrib import admin
from .models import Category, Product
from .models import Shopkeeper

# Admin panel ko thoda sundar banate hain
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Admin screen par ye saari cheezein dikhengi
    list_display = ('name', 'category', 'original_price', 'current_price', 'expiry_time')
    list_filter = ('category',) # Side mein filter aa jayega
    search_fields = ('name',)    # Search bar mil jayega

admin.site.register(Category)
admin.site.register(Shopkeeper)