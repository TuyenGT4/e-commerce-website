from django.db import models
from store.models import Product
from userauths.models import User

TYPE = (
    ("New Order", "Đơn hàng mới"),
    ("Item Shipped", "Hàng đang giao"),
    ("Item Delivered", "Đã giao hàng"),
)


class Wishlist(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Khách hàng"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name="wishlist",
        verbose_name="Sản phẩm"
    )

    def __str__(self):
        if self.product.name:
            return self.product.name
        else:
            return "Yêu thích"

    class Meta:
        verbose_name = "Yêu thích"
        verbose_name_plural = "Danh sách yêu thích"


class Address(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True,
        verbose_name="Khách hàng"
    )
    full_name = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        default=None,
        verbose_name="Họ và tên"
    )
    mobile = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        default=None,
        verbose_name="Số điện thoại"
    )
    email = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        default=None,
        verbose_name="Email"
    )
    country = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        default=None,
        verbose_name="Quốc gia"
    )
    state = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        default=None,
        verbose_name="Tỉnh/Thành phố"
    )
    city = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        default=None,
        verbose_name="Quận/Huyện"
    )
    address = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        default=None,
        verbose_name="Địa chỉ cụ thể"
    )
    zip_code = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        default=None,
        verbose_name="Mã bưu chính"
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Địa chỉ"
        verbose_name_plural = "Địa chỉ khách hàng"


class Notifications(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True,
        verbose_name="Khách hàng"
    )
    type = models.CharField(
        max_length=100, 
        choices=TYPE, 
        default=None,
        verbose_name="Loại thông báo"
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
        verbose_name_plural = "Thông báo khách hàng"