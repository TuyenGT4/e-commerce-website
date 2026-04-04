from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from userauths import models as userauths_models


@admin.register(userauths_models.User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'username']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']

    # Việt hóa tên các nhóm field trong trang chi tiết
    fieldsets = (
        ('Thông tin đăng nhập', {
            'fields': ('email', 'username', 'password')
        }),
        ('Phân quyền', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Thời gian', {
            'fields': ('date_joined', 'last_login')
        }),
    )

    # Fieldsets khi tạo user mới
    add_fieldsets = (
        ('Tạo tài khoản mới', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )


@admin.register(userauths_models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'mobile', 'user_type']
    list_filter = ['user_type']
    search_fields = ['full_name', 'user__email', 'mobile']
    ordering = ['user__date_joined']
    readonly_fields = ['user']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('user', 'full_name', 'image', 'mobile')
        }),
        ('Loại tài khoản', {
            'fields': ('user_type',)
        }),
    )


@admin.register(userauths_models.ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'subject', 'date', 'is_read']
    list_filter = ['is_read', 'date']
    search_fields = ['full_name', 'email', 'subject']
    ordering = ['-date']
    readonly_fields = ['full_name', 'email', 'phone', 'subject', 'message', 'date']

    # Cho phép đánh dấu đã đọc trực tiếp từ danh sách
    list_editable = ['is_read']

    fieldsets = (
        ('Thông tin người gửi', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Nội dung', {
            'fields': ('subject', 'message')
        }),
        ('Trạng thái', {
            'fields': ('date', 'is_read')
        }),
    )

    # Action đánh dấu đã đọc / chưa đọc hàng loạt
    actions = ['danh_dau_da_doc', 'danh_dau_chua_doc']

    @admin.action(description='Đánh dấu đã đọc')
    def danh_dau_da_doc(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} tin nhắn đã được đánh dấu là đã đọc.')

    @admin.action(description='Đánh dấu chưa đọc')
    def danh_dau_chua_doc(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} tin nhắn đã được đánh dấu là chưa đọc.')


# Việt hóa tên trang Admin
admin.site.site_header = "Quản trị hệ thống"
admin.site.site_title = "Trang quản trị"
admin.site.index_title = "Chào mừng đến trang quản trị"