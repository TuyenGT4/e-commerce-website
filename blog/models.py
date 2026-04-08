from django.db import models
from userauths import models as userauths_models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone

STATUS_CHOICES = [
    ('Draft', 'Bản nháp'),
    ('Published', 'Đã đăng'),
]


class Category(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Tên danh mục"
    )
    slug = models.SlugField(
        max_length=150, 
        unique=True, 
        blank=True,
        verbose_name="Đường dẫn"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục bài viết"


class Blog(models.Model):
    image = models.ImageField(
        upload_to='blog_images', 
        blank=True, 
        null=True,
        verbose_name="Ảnh bìa"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Tiêu đề"
    )
    slug = models.SlugField(
        max_length=350, 
        unique=True, 
        blank=True,
        verbose_name="Đường dẫn"
    )
    author = models.ForeignKey(
        userauths_models.User, 
        on_delete=models.CASCADE,
        verbose_name="Tác giả"
    )
    content = CKEditor5Field(
        config_name='extends', 
        null=True, 
        blank=True,
        verbose_name="Nội dung"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Danh mục"
    )
    tags = models.CharField(
        max_length=200, 
        null=True, 
        blank=True,
        verbose_name="Thẻ tag"
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default="Published",
        verbose_name="Trạng thái"
    )
    likes = models.ManyToManyField(
        userauths_models.User, 
        blank=True, 
        related_name="likes",
        verbose_name="Lượt thích"
    )
    views = models.PositiveIntegerField(
        default=0,
        verbose_name="Lượt xem"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Bài viết nổi bật"
    )
    date = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày đăng"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def total_likes(self):
        return self.likes.all().count()

    class Meta:
        verbose_name = "Bài viết"
        verbose_name_plural = "Bài viết"


class Comment(models.Model):
    blog = models.ForeignKey(
        Blog, 
        on_delete=models.CASCADE, 
        related_name="comments",
        verbose_name="Bài viết"
    )
    full_name = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Họ và tên"
    )
    email = models.EmailField(
        null=True, 
        blank=True,
        verbose_name="Email"
    )
    content = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Nội dung bình luận"
    )
    approved = models.BooleanField(
        default=False,
        verbose_name="Đã duyệt"
    )
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Ngày bình luận"
    )

    def __str__(self):
        return f"Bình luận của {self.full_name} về {self.blog.title}"

    class Meta:
        verbose_name = "Bình luận"
        verbose_name_plural = "Bình luận bài viết"