from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


USER_TYPE = (
    ("Vendor", "Nhà bán hàng"),
    ("Customer", "Khách hàng"),
)

class User(AbstractUser):
    username = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name="Tên đăng nhập"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        email_username, _ = self.email.split('@')
        if self.username == "" or self.username == None:
            self.username = email_username
        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"


class Profile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Tài khoản"
    )
    image = models.ImageField(
        upload_to='accounts/users', 
        default='default/default-user.jpg', 
        null=True, 
        blank=True,
        verbose_name="Ảnh đại diện"
    )
    full_name = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name="Họ và tên"
    )
    mobile = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name="Số điện thoại"
    )
    user_type = models.CharField(
        max_length=255, 
        choices=USER_TYPE, 
        null=True, 
        blank=True, 
        default=None,
        verbose_name="Loại tài khoản"
    )

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.full_name == "" or self.full_name == None:
            self.full_name = self.user.full_name
        super(Profile, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Hồ sơ"
        verbose_name_plural = "Hồ sơ người dùng"


    

class ContactMessage(models.Model):
    full_name = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name="Họ và tên"
    )
    email = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name="Email"
    )
    subject = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        verbose_name="Tiêu đề"
    )
    message = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Nội dung"
    )
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Ngày gửi"
    )

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['-date']
        verbose_name = "Tin nhắn liên hệ"
        verbose_name_plural = "Tin nhắn liên hệ"
    