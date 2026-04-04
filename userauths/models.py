from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator

USER_TYPE = (
    ("Vendor", "Người bán"),
    ("Customer", "Khách hàng"),
)

# Validator số điện thoại 
phone_validator = RegexValidator(
    regex=r'^(0[3|5|7|8|9])+([0-9]{8})$',
    message="Số điện thoại không hợp lệ. Vui lòng nhập số điện thoại Việt Nam (VD: 0912345678)"
)

class User(AbstractUser):
    username = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tên đăng nhập")
    email = models.EmailField(unique=True, verbose_name="Email")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
      verbose_name = "Người dùng"
      verbose_name_plural = "Người dùng"
        
    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Tự động tạo username từ phần trước @ của email
        if not self.username:
            email_username, _ = self.email.split('@')
            self.username = email_username
        super(User, self).save(*args, **kwargs)
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Người dùng")
    image = models.ImageField(upload_to='accounts/users', default='default/default-user.jpg', null=True, blank=True, verbose_name="Ảnh đại diện")
    full_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Họ và tên")
    mobile = models.CharField(max_length=255, null=True, blank=True, validators=[phone_validator], verbose_name="Số điện thoại")
    user_type = models.CharField(max_length=255, choices=USER_TYPE, null=True, blank=True, default=None, verbose_name="Loại tài khoản")
    class Meta:
        verbose_name = "Hồ sơ"
        verbose_name_plural = "Hồ sơ người dùng"
        
    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.user.username or self.user.email
        super(Profile, self).save(*args, **kwargs)

    

class ContactMessage(models.Model):
    full_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Họ và tên")
    email = models.EmailField(max_length=255, null=True, blank=True,  verbose_name="Email")
    phone = models.CharField(max_length=15, null=True, blank=True, validators=[phone_validator], verbose_name="Số điện thoại")
    subject = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tiêu đề")
    message = models.TextField(null=True, blank=True,  verbose_name="Nội dung")
    date = models.DateTimeField(default=timezone.now, verbose_name="Ngày gửi")
    is_read = models.BooleanField(default=False,verbose_name="Đã đọc")
    def __str__(self):
        return self.full_name
    
    class Meta:
        ordering = ['-date']
        verbose_name = "Tin nhắn liên hệ"
        verbose_name_plural = "Tin nhắn liên hệ"

    