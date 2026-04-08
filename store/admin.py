from django.contrib import admin
from store import models as store_models


class GalleryInline(admin.TabularInline):
    model = store_models.Gallery
    extra = 1
    verbose_name = "Ảnh"
    verbose_name_plural = "Thư viện ảnh"


class VariantInline(admin.TabularInline):
    model = store_models.Variant
    extra = 1
    verbose_name = "Biến thể"
    verbose_name_plural = "Biến thể sản phẩm"


class VariantItemInline(admin.TabularInline):
    model = store_models.VariantItem
    extra = 1
    verbose_name = "Thuộc tính"
    verbose_name_plural = "Chi tiết biến thể"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'image']
    list_editable = ['image']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
    verbose_name = "Danh mục"


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 
        'regular_price', 'stock', 
        'status', 'featured', 'vendor', 'date'
    ]
    search_fields = ['name', 'category__title', 'vendor__username']
    list_filter = ['status', 'featured', 'category']
    list_editable = ['status', 'featured']
    inlines = [GalleryInline, VariantInline]
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'date'
    readonly_fields = ['sku', 'date']
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'category', 'vendor', 'image', 'description')
        }),
        ('Giá & Tồn kho', {
            'fields': ('price', 'regular_price', 'stock', 'shipping')
        }),
        ('Trạng thái', {
            'fields': ('status', 'featured')
        }),
        ('Thông tin hệ thống', {
            'fields': ('sku', 'slug', 'date'),
            'classes': ('collapse',)
        }),
    )


class VariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'name']
    search_fields = ['product__name', 'name']
    inlines = [VariantItemInline]


class VariantItemAdmin(admin.ModelAdmin):
    list_display = ['variant', 'title', 'content']
    search_fields = ['variant__name', 'title']


class GalleryAdmin(admin.ModelAdmin):
    list_display = ['product', 'gallery_id']
    search_fields = ['product__name', 'gallery_id']
    readonly_fields = ['gallery_id']


class CartAdmin(admin.ModelAdmin):
    list_display = [
        'cart_id', 'product', 'user', 
        'qty', 'price', 'total', 'date'
    ]
    search_fields = ['cart_id', 'product__name', 'user__username']
    list_filter = ['date']
    date_hierarchy = 'date'
    readonly_fields = ['cart_id', 'date']


class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'vendor', 'discount']
    search_fields = ['code', 'vendor__username']
    list_filter = ['vendor']


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'customer', 'total',
        'payment_status', 'order_status',
        'payment_method', 'date'
    ]
    list_editable = ['payment_status', 'order_status', 'payment_method']
    search_fields = ['order_id', 'customer__username', 'customer__email']
    list_filter = ['payment_status', 'order_status', 'payment_method']
    date_hierarchy = 'date'
    readonly_fields = ['order_id', 'date', 'payment_id']
    fieldsets = (
        ('Thông tin đơn hàng', {
            'fields': ('order_id', 'customer', 'address', 'date')
        }),
        ('Thanh toán', {
            'fields': (
                'payment_status', 'payment_method', 
                'payment_id', 'order_status'
            )
        }),
        ('Chi phí', {
            'fields': (
                'sub_total', 'shipping', 'tax',
                'service_fee', 'total',
                'initial_total', 'saved'
            )
        }),
        ('Mã giảm giá & Nhà bán hàng', {
            'fields': ('coupons', 'vendors'),
            'classes': ('collapse',)
        }),
    )


class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'item_id', 'order', 'product',
        'qty', 'price', 'total',
        'order_status', 'shipping_service', 'tracking_id'
    ]
    list_editable = ['order_status', 'shipping_service', 'tracking_id']
    search_fields = ['item_id', 'order__order_id', 'product__name']
    list_filter = ['order_status', 'shipping_service']
    date_hierarchy = 'date'
    readonly_fields = ['item_id', 'date']
    fieldsets = (
        ('Thông tin sản phẩm', {
            'fields': (
                'order', 'product', 'vendor',
                'qty', 'color', 'size'
            )
        }),
        ('Chi phí', {
            'fields': (
                'price', 'sub_total', 'shipping',
                'tax', 'total', 'initial_total', 'saved'
            )
        }),
        ('Vận chuyển', {
            'fields': (
                'order_status', 'shipping_service', 'tracking_id'
            )
        }),
        ('Mã giảm giá', {
            'fields': ('coupon', 'applied_coupon'),
            'classes': ('collapse',)
        }),
        ('Thông tin hệ thống', {
            'fields': ('item_id', 'date'),
            'classes': ('collapse',)
        }),
    )


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'active', 'date']
    list_editable = ['active']
    search_fields = ['user__username', 'product__name']
    list_filter = ['active', 'rating']
    date_hierarchy = 'date'
    readonly_fields = ['date']


admin.site.register(store_models.Category, CategoryAdmin)
admin.site.register(store_models.Product, ProductAdmin)
admin.site.register(store_models.Variant, VariantAdmin)
admin.site.register(store_models.VariantItem, VariantItemAdmin)
admin.site.register(store_models.Gallery, GalleryAdmin)
admin.site.register(store_models.Cart, CartAdmin)
admin.site.register(store_models.Coupon, CouponAdmin)
admin.site.register(store_models.Order, OrderAdmin)
admin.site.register(store_models.OrderItem, OrderItemAdmin)
admin.site.register(store_models.Review, ReviewAdmin)