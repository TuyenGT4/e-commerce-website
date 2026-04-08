from django.contrib import admin
from userauths import models as userauths_models


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']
    search_fields = ['username', 'email']
    verbose_name = "Người dùng"


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'mobile', 'user_type']
    search_fields = ['user__email', 'full_name', 'mobile']
    list_filter = ['user_type']


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject', 'date']
    search_fields = ['full_name', 'email', 'subject']
    readonly_fields = ['full_name', 'email', 'subject', 'message', 'date']
    date_hierarchy = 'date'


# Tùy chỉnh tiêu đề Admin
admin.site.site_header = "Quản trị hệ thống"
admin.site.site_title = "Trang quản trị"
admin.site.index_title = "Chào mừng đến trang quản trị"

admin.site.register(userauths_models.User, UserAdmin)
admin.site.register(userauths_models.Profile, ProfileAdmin)
admin.site.register(userauths_models.ContactMessage, ContactMessageAdmin)