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
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    original_price = models.FloatField()
    expiry_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add = True)

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

        # --------CATEGORY-BASED DECAY LOGIC--------
        cat_name = self.category.name.lower()

        # 1. PREMIUM DAIRY (Fast, Hourly, Linear)
        if 'dairy' in cat_name or 'fresh' in cat_name:
            
            # Cheese/Paneer: Consistent hourly drop
            final_price = self.original_price * (1 - (self.category.decay_rate * hours_passed))

        # 2. REGIONAL SPECIALTIES / SWEETS (Exponential Crash)
        elif 'regional' in cat_name or 'sweets' in cat_name:
            
            # Nashik Sweets: Price stays stable, then crashes 
            # Math: Original * (Remaining Ratio ** 1.5)
            final_price = self.original_price * (remaining_ratio ** 1.5)

        # 3. BABY CARE & HEALTH (Steady, Trust-based)
        elif 'baby' in cat_name or 'health' in cat_name:
            
            # Slow Daily Decay (Never goes below 50% for quality trust)
            discount = self.original_price * (self.category.decay_rate * days_passed)
            final_price = max(self.original_price - discount, self.original_price * 0.5)

        # 4. GOURMET / IMPORTED (Daily Linear)
        elif 'gourmet' in cat_name or 'imported' in cat_name:
            
            # Olive Oil/Coffee: Drops by the day
            discount = self.original_price * (self.category.decay_rate * days_passed)
            final_price = self.original_price - discount

        # 5. DEFAULT LOGIC (Baaki bache huye products ke liye)
        else:
            # Pehle check karo: Ghante (H) ginn-ne hain ya Din (D)?
            if self.category.decay_unit == 'H':
                samay = hours_passed
            else:
                samay = days_passed
            
            # Simple Formula: Original Price - (Price * Rate * Samay)
            total_discount = self.original_price * self.category.decay_rate * samay
            final_price = self.original_price - total_discount


        # Minimum price floor: 15% of original price to ensure it's not too cheap
        floor_price = self.original_price * 0.15
        return round(max(final_price, floor_price), 2)
    
class Shopkeeper(models.Model):
    # User ki personal details
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True) # Unique taaki ek email se do dukan na bane
    
    # Dukan ki details
    shop_name = models.CharField(max_length=200)
    address = models.TextField()
    
    # Login ke liye (Abhi ke liye simple password rakh rahe hain)
    password = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True) # Kab register kiya

    def __str__(self):
        return f"{self.shop_name} - {self.full_name}"