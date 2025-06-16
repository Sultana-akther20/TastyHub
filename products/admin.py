from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import TextInput, Textarea
from .models import Category, Product, ProductImage, ProductReview

class ProductImageInline(admin.TabularInline):
    """Inline admin for product images"""
    model = ProductImage
    extra = 1
    fields = ('image', 'image_preview', 'alt_text', 'order')
    readonly_fields = ('image_preview',)
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '40'})},
    }
    
    def image_preview(self, obj):
        """Show image preview in admin"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model"""
    list_display = ('name', 'parent', 'is_active', 'order', 'product_count')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Display Options', {
            'fields': ('is_active', 'order')
        }),
    )
    
    def product_count(self, obj):
        """Display number of menu items in this category"""
        count = obj.products.count()
        if count > 0:
            return format_html(
                '<strong>{}</strong>',
                count
            )
        return count
    product_count.short_description = 'Menu Items'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('parent').prefetch_related('products')







@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model"""
    list_display = (
        'name', 'category', 'formatted_price', 'is_available', 
        'is_featured', 'preparation_time_display', 'image_preview'
    )
    list_filter = (
        'is_available', 'is_featured', 'category'
    )
    search_fields = ('name', 'description', 'ingredients')
    list_editable = ('is_available', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-is_featured', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'is_available', 'is_featured')
        }),
        ('Dish Details', {
            'fields': ('preparation_time', 'ingredients')
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
    )
    
    readonly_fields = ('image_preview',)
    inlines = [ProductImageInline]
    
    # Custom form field widgets
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 80})},
    }
    
    def image_preview(self, obj):
        """Show image preview in admin"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'
    
    def formatted_price(self, obj):
        """Display formatted price"""
        return obj.formatted_price
    formatted_price.short_description = 'Price'
    formatted_price.admin_order_field = 'price'
    
    def preparation_time_display(self, obj):
        """Display preparation time"""
        return obj.preparation_time_display
    preparation_time_display.short_description = 'Prep Time'
    preparation_time_display.admin_order_field = 'preparation_time'
    
    def get_queryset(self, request):
        """Optimize queries"""
        return super().get_queryset(request).select_related('category')
    
    actions = ['mark_as_featured', 'mark_as_not_featured', 'mark_as_available', 'mark_as_unavailable']
    
    def mark_as_featured(self, request, queryset):
        """Mark selected items as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} menu items marked as featured.')
    mark_as_featured.short_description = 'Mark selected items as featured'
    
    def mark_as_not_featured(self, request, queryset):
        """Mark selected items as not featured"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} menu items marked as not featured.')
    mark_as_not_featured.short_description = 'Mark selected items as not featured'
    
    def mark_as_available(self, request, queryset):
        """Mark selected items as available"""
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} menu items marked as available.')
    mark_as_available.short_description = 'Mark selected items as available'
    
    def mark_as_unavailable(self, request, queryset):
        """Mark selected items as unavailable"""
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} menu items marked as unavailable.')
    mark_as_unavailable.short_description = 'Mark selected items as unavailable'  



@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for ProductImage model"""
    list_display = ('product', 'image_preview', 'alt_text', 'order', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'alt_text')
    list_editable = ('order',)
    ordering = ('product', 'order')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        """Show image preview in admin"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Admin configuration for ProductReview model"""
    list_display = ('product', 'customer_name', 'star_rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('product__name', 'customer_name', 'customer_email', 'comment')
    list_editable = ('is_approved',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'customer_name', 'customer_email', 'rating')
        }),
        ('Review Content', {
            'fields': ('comment', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def star_rating(self, obj):
        """Display star rating"""
        return format_html(
            '<span style="color: #ffc107;">{}</span>',
            obj.star_display
        )
    star_rating.short_description = 'Rating'
    star_rating.admin_order_field = 'rating'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        """Approve selected reviews"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved.')
    approve_reviews.short_description = 'Approve selected reviews'
    
    def disapprove_reviews(self, request, queryset):
        """Disapprove selected reviews"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews disapprove.')
    disapprove_reviews.short_description = 'Disapprove selected reviews'

# Customize admin site header and title
admin.site.site_header = "TastyHub Restaurant Admin"
admin.site.site_title = "TastyHub Admin"
admin.site.index_title = "Restaurant Management Dashboard"