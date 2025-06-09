from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """
    Category model for organizing products hierarchically
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='subcategories'
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})
    
    @property
    def is_parent(self):
        """Check if this category has subcategories"""
        return self.subcategories.exists()
    
    @property
    def get_all_children(self):
        """Get all subcategories recursively"""
        children = []
        for child in self.subcategories.filter(is_active=True):
            children.append(child)
            children.extend(child.get_all_children)
        return children


class Product(models.Model):
    """
    Product model for menu items
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE,
        related_name='products'
    )
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Availability and featured status
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Additional product details
    preparation_time = models.PositiveIntegerField(
        help_text="Preparation time in minutes",
        validators=[MinValueValidator(1)]
    )
    ingredients = models.TextField(
        help_text="List of ingredients used in this product"
    )
    calories = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Calories per serving"
    )
    
    # SEO and URL
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)
    
    # Image field - assuming images are in media folder of another app
    # Adjust the upload_to path based on your media structure
    image = models.ImageField(
        upload_to='products/images/', 
        null=True, 
        blank=True,
        help_text="Product image"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    # Stock management (optional)
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Available stock quantity"
    )
    track_stock = models.BooleanField(
        default=False,
        help_text="Whether to track stock for this product"
    )
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-is_featured', 'category__order', 'name']
        indexes = [
            models.Index(fields=['is_available', 'is_featured']),
            models.Index(fields=['category', 'is_available']),
        ]
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    @property
    def is_in_stock(self):
        """Check if product is in stock (if stock tracking is enabled)"""
        if not self.track_stock:
            return self.is_available
        return self.is_available and self.stock_quantity > 0
    
    @property
    def formatted_price(self):
        """Return formatted price with currency symbol"""
        return f"${self.price}"
    
    @property
    def preparation_time_display(self):
        """Return formatted preparation time"""
        if self.preparation_time == 1:
            return "1 minute"
        return f"{self.preparation_time} minutes"


class ProductImage(models.Model):
    """
    Model for additional product images
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='additional_images'
    )
    image = models.ImageField(
        upload_to='products/gallery/',
        help_text="Additional product image"
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Alternative text for accessibility"
    )
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"


class ProductReview(models.Model):
    """
    Model for customer reviews (optional)
    """
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
        unique_together = ['product', 'customer_email']  # One review per email per product
    
    def __str__(self):
        return f"{self.product.name} - {self.rating} stars by {self.customer_name}"


# Optional: Nutritional Information Model
class NutritionalInfo(models.Model):
    """
    Detailed nutritional information for products
    """
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='nutrition'
    )
    
    # Nutritional values per serving
    calories = models.PositiveIntegerField(null=True, blank=True)
    protein = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Grams")
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Grams")
    fat = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Grams")
    fiber = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Grams")
    sugar = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Grams")
    sodium = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Milligrams")
    
    # Allergen information
    contains_gluten = models.BooleanField(default=False)
    contains_dairy = models.BooleanField(default=False)
    contains_nuts = models.BooleanField(default=False)
    contains_eggs = models.BooleanField(default=False)
    contains_soy = models.BooleanField(default=False)
    
    vegetarian = models.BooleanField(default=False)
    vegan = models.BooleanField(default=False)
    gluten_free = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Nutritional Information"
        verbose_name_plural = "Nutritional Information"
    
    def __str__(self):
        return f"Nutrition info for {self.product.name}"