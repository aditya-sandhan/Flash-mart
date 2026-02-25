import urllib.parse
from django.db import models
from django.utils import timezone
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    decay_rate  = models.FloatField(help_text="Decay rate per unit time (e.g., 0.1 for 10% per hour)")
    decay_unit = models.CharField(max_length=1, choices=[('H', 'Hourly'), ('D', 'Daily')]) # Fixed choices so that there is no error in input
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name.capitalize() #Hamesha First letter Capital dikhayega
    

class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    # Shopkeeper link add kiya
    shopkeeper = models.ForeignKey('Shopkeeper', on_delete=models.CASCADE, related_name='products', null=True)
    
    # Category ko filhal allow null kiya taaki tera current form chal sake bina crash hue
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True) 
    
    original_price = models.FloatField()
    expiry_time = models.DateTimeField() # Name kept as expiry_time
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def image_url(self):
        """
        Generates a professional Typography Placeholder image.
        Uses Category for background colors and Product Name for text.
        """
        import urllib.parse
        
        # Naam ko format karo (Sirf pehle 2 words lenge taaki image clean lage)
        if self.name:
            words = self.name.split()[:2]
            display_text = " ".join(words)
            safe_text = urllib.parse.quote(display_text)
        else:
            safe_text = "Item"

      
        bg_color = "F8F9FA"
        if self.category:
            cat_name = self.category.name.lower()
            if 'dairy' in cat_name or 'fresh' in cat_name:
                bg_color = "E3F2FD" 
            elif 'sweet' in cat_name or 'regional' in cat_name:
                bg_color = "FCE4EC" 
            elif 'health' in cat_name or 'baby' in cat_name:
                bg_color = "E8F5E9" 
            elif 'gourmet' in cat_name:
                bg_color = "FFF8E1" 

        # Professional typography image API
        return f"https://placehold.co/400x400/{bg_color}/212529?text={safe_text}&font=Montserrat"

    @property
    def time_left(self):
        now = timezone.now()
        if now >= self.expiry_time:
            return "Expired"
        
        delta = self.expiry_time - now
        total_hours = int(delta.total_seconds() // 3600)
        days = delta.days

        if not self.category or self.category.decay_unit == 'H':
            return f"Ends in {total_hours}h"
        else:
            return f"Ends in {max(1, days)}d"

    @property
    def current_price(self):
        now = timezone.now()
        if now >= self.expiry_time:
            return 0.0
        
        total_life =(self.expiry_time - self.created_at).total_seconds() 
        passed_life = (now - self.created_at).total_seconds()
        remaining_ratio = 1 - (passed_life / total_life) if total_life > 0 else 0

        hours_passed = passed_life / 3600
        days_passed = passed_life / (3600 * 24)

        #  THE SAFETY NET: Agar Category NAHI hai toh crash mat karo!
        if self.category is None:
            # Default 5% hourly discount if no category is assigned yet
            total_discount = self.original_price * 0.05 * hours_passed
            final_price = self.original_price - total_discount
            
        else:
            # --------CATEGORY-BASED DECAY LOGIC--------
            cat_name = self.category.name.lower()

            if 'dairy' in cat_name or 'fresh' in cat_name:
                final_price = self.original_price * (1 - (self.category.decay_rate * hours_passed))

            elif 'regional' in cat_name or 'sweets' in cat_name:
                final_price = self.original_price * (remaining_ratio ** 1.5)

            elif 'baby' in cat_name or 'health' in cat_name:
                discount = self.original_price * (self.category.decay_rate * days_passed)
                final_price = max(self.original_price - discount, self.original_price * 0.5)

            elif 'gourmet' in cat_name or 'imported' in cat_name:
                discount = self.original_price * (self.category.decay_rate * days_passed)
                final_price = self.original_price - discount

            else:
                if self.category.decay_unit == 'H':
                    samay = hours_passed
                else:
                    samay = days_passed
                total_discount = self.original_price * self.category.decay_rate * samay
                final_price = self.original_price - total_discount

        # Minimum price floor: 15% of original price
        floor_price = self.original_price * 0.15
        return round(max(final_price, floor_price), 2)
    
    
class Shopkeeper(models.Model):
    # User ki personal details
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True) 
    
    # Dukan ki details
    shop_name = models.CharField(max_length=200)
    address = models.TextField()
    
    # Login ke liye
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.shop_name} - {self.full_name}"
    

class Customer(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    locked_price = models.FloatField()
    order_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Reserved') # Status can be: Reserved, Picked Up, Cancelled

    def __str__(self):
        return f"{self.customer.full_name} grabbed {self.product.name} @ ₹{self.locked_price}"