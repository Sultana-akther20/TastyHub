from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    """
    Category model for organizing products hierarchically
    """
    name = models.CharField(max_length=200, unique=True)
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
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    
    
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
    is_available = models.BooleanField(default=True, help_text="Is this item currently available?")
    is_featured = models.BooleanField(default=False, help_text="Display as featured item")
    
    # Additional product details
    preparation_time = models.PositiveIntegerField(
        help_text="Preparation time in minutes",
        validators=[MinValueValidator(1)]
    )
    ingredients = models.TextField(
        help_text="List of ingredients used in this dish"
    )
    
    # SEO and URL
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)
    
    image = models.URLField(
    max_length=1000,  # large enough for Cloudinary URLs
    null=True, 
    blank=True,
    help_text="Dish image URL"
)

    
    class Meta:
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        ordering = ['-is_featured', 'category__order', 'name']
        indexes = [
            models.Index(fields=['is_available', 'is_featured']),
            models.Index(fields=['category', 'is_available']),
        ]
        
    def _str_(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    @property
    def formatted_price(self):
        """Return formatted price with currency symbol"""
        return f"£{self.price}"
    
    @property
    def preparation_time_display(self):
        """Return formatted preparation time"""
        if self.preparation_time == 1:
            return "1 minute"
        return f"{self.preparation_time} minutes"

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
        help_text="Additional dish image"
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
    Model for customer reviews
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
    customer_name = models.CharField(max_length=200)
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
        verbose_name = "Customer Review"
        verbose_name_plural = "Customer Reviews"
        unique_together = ['product', 'customer_email'] 
    
    def __str__(self):
        return f"{self.product.name} - {self.rating} stars by {self.customer_name}"
    
    @property
    def star_display(self):
        """Return star rating as symbols"""
        return '★' * self.rating + '☆' * (5 - self.rating)

class Contact(models.Model):
    """
    Model for contact form submissions and complaints
    """
    
    INQUIRY_TYPES = [
        ('food_quality', 'Food Quality Issue'),
        ('delivery', 'Delivery Problem'),
        ('service', 'Service Complaint'),
        ('billing', 'Billing Issue'),
        ('suggestion', 'Suggestion'),
        ('compliment', 'Compliment'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    order_reference = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Admin fields
    admin_notes = models.TextField(blank=True, null=True, help_text="Internal notes for staff")
    resolved_by = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.get_inquiry_type_display()})"
    
    @property
    def is_complaint(self):
        """Check if this is a complaint type inquiry"""
        complaint_types = ['food_quality', 'delivery', 'service', 'billing']
        return self.inquiry_type in complaint_types
    
    @property
    def days_since_submitted(self):
        """Calculate days since submission"""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days
