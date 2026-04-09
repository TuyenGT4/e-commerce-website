from django.db import models
from shortuuid.django_fields import ShortUUIDField
from userauths.models import User
from django.utils.text import slugify

PAYOUT_METHOD = (
    ("Chuyển khoản ngân hàng", "Chuyển khoản ngân hàng"),
    ("VNPay", "VNPay"),
    ("MoMo", "MoMo"),
)

TYPE = (
    ("New Order", "Đơn hàng mới"),
    ("New Review", "Đánh giá mới"),
    ("Item Shipped", "Hàng đang giao"),
    ("Item Delivered", "Đã giao hàng"),
)


class Vendor(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="vendor",
        verbose_name="Tài khoản"
    )
    image = models.ImageField(
        upload_to="images", 
        default="shop-image.jpg", 
        blank=True,
        verbose_name="Ảnh cửa hàng"
    )
    store_name = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Tên cửa hàng"
    )
    description = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Mô tả cửa hàng"
    )
    country = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Quốc gia"
    )
    vendor_id = ShortUUIDField(
        unique=True, 
        length=6, 
        max_length=20, 
        alphabet="1234567890",
        verbose_name="Mã nhà bán hàng"
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tham gia"
    )
    slug = models.SlugField(
        blank=True, 
        null=True,
        verbose_name="Đường dẫn"
    )

    def __str__(self):
        return str(self.store_name)

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.store_name)
        super(Vendor, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Nhà bán hàng"
        verbose_name_plural = "Nhà bán hàng"


class Payout(models.Model):
    vendor = models.ForeignKey(
        Vendor, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Nhà bán hàng"
    )
    item = models.ForeignKey(
        "store.OrderItem", 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="item",
        verbose_name="Sản phẩm"
    )
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=0, 
        default=0,
        verbose_name="Số tiền thanh toán (đ)"
    )
    payout_id = ShortUUIDField(
        unique=True, 
        length=6, 
        max_length=10, 
        alphabet="1234567890",
        verbose_name="Mã thanh toán"
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name="Ngày thanh toán"
    )

    def __str__(self):
        return str(self.vendor)

    class Meta:
        ordering = ['-date']
        verbose_name = "Thanh toán cho nhà bán hàng"
        verbose_name_plural = "Thanh toán cho nhà bán hàng"

class BankAccount(models.Model):
    vendor = models.OneToOneField(
        Vendor, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Nhà bán hàng"
    )
    account_type = models.CharField(
        max_length=50, 
        choices=PAYOUT_METHOD, 
        null=True, 
        blank=True, 
        default="Chuyển khoản ngân hàng",
        verbose_name="Hình thức thanh toán"
    )
    bank_name = models.CharField(
        max_length=500,
        verbose_name="Tên ngân hàng"
    )
    account_number = models.CharField(
        max_length=100,
        verbose_name="Số tài khoản"
    )
    account_name = models.CharField(
        max_length=100,
        verbose_name="Tên chủ tài khoản"
    )
    bank_code = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Mã ngân hàng"
    )
    stripe_id = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Stripe ID"
    )
    paypal_address = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Địa chỉ PayPal"
    )

    def __str__(self):
        return self.bank_name

    class Meta:
        verbose_name = "Tài khoản ngân hàng"
        verbose_name_plural = "Tài khoản ngân hàng"


class Notifications(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        related_name="vendor_notifications",
        verbose_name="Nhà bán hàng"
    )
    type = models.CharField(
        max_length=100, 
        choices=TYPE, 
        default=None,
        verbose_name="Loại thông báo"
    )
    order = models.ForeignKey(
        "store.OrderItem", 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Đơn hàng"
    )
    seen = models.BooleanField(
        default=False,
        verbose_name="Đã xem"
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày thông báo"
    )

    def __str__(self):
        return self.type

    class Meta:
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo nhà bán hàng"