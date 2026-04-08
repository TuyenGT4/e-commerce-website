from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

from userauths import models as user_models
from vendor import models as vendor_models

import shortuuid

STATUS = (
    ("Published", "Đang bán"),
    ("Draft", "Bản nháp"),
    ("Disabled", "Đã ẩn"),
)

PAYMENT_STATUS = (
    ("Paid", "Đã thanh toán"),
    ("Processing", "Đang xử lý"),
    ("Failed", "Thất bại"),
)

PAYMENT_METHOD = (
    ("COD", "Thanh toán khi nhận hàng (COD)"),
    ("VNPay", "VNPay"),
    ("VietQR", "Quét mã QR"),
)

ORDER_STATUS = (
    ("Pending", "Chờ xử lý"),
    ("Processing", "Đang xử lý"),
    ("Shipped", "Đang giao hàng"),
    ("Fulfilled", "Đã giao hàng"),
    ("Cancelled", "Đã hủy"),
)

SHIPPING_SERVICE = (
    ("GHN", "Giao Hàng Nhanh (GHN)"),
    ("ViettelPost", "Viettel Post"),
)

RATING = (
    (1, "★☆☆☆☆ - Rất tệ"),
    (2, "★★☆☆☆ - Tệ"),
    (3, "★★★☆☆ - Bình thường"),
    (4, "★★★★☆ - Tốt"),
    (5, "★★★★★ - Xuất sắc"),
)


class Category(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name="Tên danh mục"
    )
    image = models.ImageField(
        upload_to="images", 
        default="category.jpg", 
        null=True, 
        blank=True,
        verbose_name="Hình ảnh"
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Đường dẫn"
    )

    def __str__(self):
        return self.title

    def products(self):
        return Product.objects.filter(category=self)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục sản phẩm"


class Product(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Tên sản phẩm"
    )
    image = models.FileField(
        upload_to="images", 
        blank=True, 
        null=True, 
        default="product.jpg",
        verbose_name="Ảnh đại diện"
    )
    description = CKEditor5Field(
        'Text', 
        config_name='extends',
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Danh mục"
    )
    price = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0, 
        null=True, 
        blank=True, 
        verbose_name="Giá bán (đ)"
    )
    regular_price = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0, 
        null=True, 
        blank=True, 
        verbose_name="Giá gốc (đ)"
    )
    stock = models.PositiveIntegerField(
        default=0, 
        null=True, 
        blank=True,
        verbose_name="Số lượng tồn kho"
    )
    shipping = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0, 
        null=True, 
        blank=True, 
        verbose_name="Phí vận chuyển (đ)"
    )
    status = models.CharField(
        choices=STATUS, 
        max_length=50, 
        default="Published",
        verbose_name="Trạng thái"
    )
    featured = models.BooleanField(
        default=False, 
        verbose_name="Nổi bật trên Marketplace"
    )
    vendor = models.ForeignKey(
        user_models.User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Nhà bán hàng"
    )
    sku = ShortUUIDField(
        unique=True, 
        length=5, 
        max_length=50, 
        prefix="SKU", 
        alphabet="1234567890",
        verbose_name="Mã SKU"
    )
    slug = models.SlugField(
        null=True, 
        blank=True,
        verbose_name="Đường dẫn"
    )
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Ngày đăng"
    )

    def __str__(self):
        return self.name

    def average_rating(self):
        return Review.objects.filter(product=self).aggregate(
            avg_rating=models.Avg('rating')
        )['avg_rating']

    def reviews(self):
        return Review.objects.filter(product=self)

    def gallery(self):
        return Gallery.objects.filter(product=self)

    def variants(self):
        return Variant.objects.filter(product=self)

    def vendor_orders(self):
        return OrderItem.objects.filter(product=self, vendor=self.vendor)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(shortuuid.uuid().lower()[:2])
        super(Product, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-id']
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"

class Variant(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        null=True,
        verbose_name="Sản phẩm"
    )
    name = models.CharField(
        max_length=1000, 
        null=True, 
        blank=True,
        verbose_name="Tên biến thể"
    )

    def items(self):
        return VariantItem.objects.filter(variant=self)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Biến thể"
        verbose_name_plural = "Biến thể sản phẩm"


class VariantItem(models.Model):
    variant = models.ForeignKey(
        Variant, 
        on_delete=models.CASCADE, 
        related_name='variant_items',
        verbose_name="Biến thể"
    )
    title = models.CharField(
        max_length=1000, 
        null=True, 
        blank=True,
        verbose_name="Tên thuộc tính"
    )
    content = models.CharField(
        max_length=1000, 
        null=True, 
        blank=True,
        verbose_name="Giá trị thuộc tính"
    )

    def __str__(self):
        return self.variant.name

    class Meta:
        verbose_name = "Chi tiết biến thể"
        verbose_name_plural = "Chi tiết biến thể"
    
class Gallery(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        null=True,
        verbose_name="Sản phẩm"
    )
    image = models.FileField(
        upload_to="images", 
        default="gallery.jpg",
        verbose_name="Hình ảnh"
    )
    gallery_id = ShortUUIDField(
        length=6, 
        max_length=10, 
        alphabet="1234567890",
        verbose_name="Mã ảnh"
    )

    def __str__(self):
        return f"{self.product.name} - hình ảnh"

    class Meta:
        verbose_name = "Ảnh sản phẩm"
        verbose_name_plural = "Thư viện ảnh sản phẩm"

class Cart(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name="Sản phẩm"
    )
    user = models.ForeignKey(
        user_models.User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Khách hàng"
    )
    qty = models.PositiveIntegerField(
        default=0, 
        null=True, 
        blank=True,
        verbose_name="Số lượng"
    )
    price = models.DecimalField(
        decimal_places=0, 
        max_digits=15, 
        default=0, 
        null=True, 
        blank=True,
        verbose_name="Đơn giá (đ)"
    )
    sub_total = models.DecimalField(
        decimal_places=0, 
        max_digits=15, 
        default=0, 
        null=True, 
        blank=True,
        verbose_name="Tạm tính (đ)"
    )
    shipping = models.DecimalField(
        decimal_places=0, 
        max_digits=15, 
        default=0, 
        null=True, 
        blank=True,
        verbose_name="Phí vận chuyển (đ)"
    )
    tax = models.DecimalField(
        decimal_places=0, 
        max_digits=15, 
        default=0, 
        null=True, 
        blank=True,
        verbose_name="Thuế VAT (đ)"
    )
    total = models.DecimalField(
        decimal_places=0, 
        max_digits=15, 
        default=0, 
        null=True, 
        blank=True,
        verbose_name="Tổng cộng (đ)"
    )
    size = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Kích cỡ"
    )
    color = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Màu sắc"
    )
    cart_id = models.CharField(
        max_length=1000, 
        null=True, 
        blank=True,
        verbose_name="Mã giỏ hàng"
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày thêm"
    )

    def __str__(self):
        return f'{self.cart_id} - {self.product.name}'

    class Meta:
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Giỏ hàng"

class Coupon(models.Model):
    vendor = models.ForeignKey(
        user_models.User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Nhà bán hàng"
    )
    code = models.CharField(
        max_length=100,
        verbose_name="Mã giảm giá"
    )
    discount = models.IntegerField(
        default=1,
        verbose_name="Mức giảm (%)"
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Mã giảm giá"
        verbose_name_plural = "Mã giảm giá"


class Order(models.Model):
    vendors = models.ManyToManyField(
        user_models.User, 
        blank=True,
        verbose_name="Nhà bán hàng"
    )
    customer = models.ForeignKey(
        user_models.User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="customer", 
        blank=True,
        verbose_name="Khách hàng"
    )
    sub_total = models.DecimalField(
        default=0, 
        max_digits=15, 
        decimal_places=0,
        verbose_name="Tạm tính (đ)"
    )
    shipping = models.DecimalField(
        default=0, 
        max_digits=15, 
        decimal_places=0,
        verbose_name="Phí vận chuyển (đ)"
    )
    tax = models.DecimalField(
        default=0, 
        max_digits=15, 
        decimal_places=0,
        verbose_name="Thuế VAT (đ)"
    )
    service_fee = models.DecimalField(
        default=0, 
        max_digits=15, 
        decimal_places=0,
        verbose_name="Phí dịch vụ (đ)"
    )
    total = models.DecimalField(
        default=0, 
        max_digits=15, 
        decimal_places=0,
        verbose_name="Tổng cộng (đ)"
    )
    payment_status = models.CharField(
        max_length=100, 
        choices=PAYMENT_STATUS, 
        default="Processing",
        verbose_name="Trạng thái thanh toán"
    )
    payment_method = models.CharField(
        max_length=100, 
        choices=PAYMENT_METHOD, 
        default=None, 
        null=True, 
        blank=True,
        verbose_name="Phương thức thanh toán"
    )
    order_status = models.CharField(
        max_length=100, 
        choices=ORDER_STATUS, 
        default="Pending",
        verbose_name="Trạng thái đơn hàng"
    )
    initial_total = models.DecimalField(
        default=0, 
        max_digits=15, 
        decimal_places=0, 
        help_text="Tổng tiền gốc trước khi áp dụng giảm giá",
        verbose_name="Tổng tiền gốc (đ)"
    )
    saved = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0, 
        null=True, 
        blank=True, 
        help_text="Số tiền khách hàng được giảm",
        verbose_name="Tiết kiệm được (đ)"
    )
    address = models.ForeignKey(
        "customer.Address", 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Địa chỉ giao hàng"
    )
    coupons = models.ManyToManyField(
        Coupon, 
        blank=True,
        verbose_name="Mã giảm giá"
    )
    order_id = ShortUUIDField(
        length=6, 
        max_length=25, 
        alphabet="1234567890",
        verbose_name="Mã đơn hàng"
    )
    payment_id = models.CharField(
        null=True, 
        blank=True, 
        max_length=1000,
        verbose_name="Mã giao dịch"
    )
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Ngày đặt hàng"
    )

    def __str__(self):
        return self.order_id

    def order_items(self):
        return OrderItem.objects.filter(order=self)

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ['-date']


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        verbose_name="Đơn hàng"
    )
    order_status = models.CharField(
        max_length=100, 
        choices=ORDER_STATUS, 
        default="Pending",
        verbose_name="Trạng thái đơn hàng"
    )
    shipping_service = models.CharField(
        max_length=100, 
        choices=SHIPPING_SERVICE, 
        default=None, 
        null=True, 
        blank=True,
        verbose_name="Đơn vị vận chuyển"
    )
    tracking_id = models.CharField(
        max_length=100, 
        default=None, 
        null=True, 
        blank=True,
        verbose_name="Mã vận đơn"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name="Sản phẩm"
    )
    qty = models.IntegerField(
        default=0,
        verbose_name="Số lượng"
    )
    color = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Màu sắc"
    )
    size = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Kích cỡ"
    )
    price = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name="Đơn giá (đ)"
    )
    sub_total = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name="Tạm tính (đ)"
    )
    shipping = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name="Phí vận chuyển (đ)"
    )
    tax = models.DecimalField(
        default=0, 
        max_digits=15, 
        decimal_places=0,
        verbose_name="Thuế VAT (đ)"
    )
    total = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name="Tổng cộng (đ)"
    )
    initial_total = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0, 
        help_text="Tổng tiền gốc trước khi áp dụng giảm giá",
        verbose_name="Tổng tiền gốc (đ)"
    )
    saved = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0, 
        null=True, 
        blank=True, 
        help_text="Số tiền khách hàng được giảm",
        verbose_name="Tiết kiệm được (đ)"
    )
    coupon = models.ManyToManyField(
        Coupon, 
        blank=True,
        verbose_name="Mã giảm giá"
    )
    applied_coupon = models.BooleanField(
        default=False,
        verbose_name="Đã áp dụng mã giảm giá"
    )
    item_id = ShortUUIDField(
        length=6, 
        max_length=25, 
        alphabet="1234567890",
        verbose_name="Mã sản phẩm"
    )
    vendor = models.ForeignKey(
        user_models.User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="vendor_order_items",
        verbose_name="Nhà bán hàng"
    )
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Ngày đặt"
    )

    def order_id(self):
        return f"{self.order.order_id}"

    def __str__(self):
        return self.item_id

    class Meta:
        ordering = ['-date']
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"

class Review(models.Model):
    user = models.ForeignKey(
        user_models.User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        verbose_name="Khách hàng"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name="reviews",
        verbose_name="Sản phẩm"
    )
    review = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Nội dung đánh giá"
    )
    reply = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Phản hồi từ cửa hàng"
    )
    rating = models.IntegerField(
        choices=RATING, 
        default=None,
        verbose_name="Số sao"
    )
    active = models.BooleanField(
        default=False,
        verbose_name="Hiển thị"
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày đánh giá"
    )

    def __str__(self):
        return f"{self.user.username} đánh giá {self.product.name}"

    class Meta:
        verbose_name = "Đánh giá"
        verbose_name_plural = "Đánh giá sản phẩm"
        
