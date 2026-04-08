from django.contrib import admin
from vendor import models as vendor_models


class VendorAdmin(admin.ModelAdmin):
    list_display = [
        'store_name', 'user', 
        'country', 'vendor_id', 'date'
    ]
    search_fields = ['store_name', 'user__username', 'vendor_id']
    prepopulated_fields = {'slug': ('store_name',)}
    list_filter = ['country', 'date']
    date_hierarchy = 'date'
    readonly_fields = ['vendor_id', 'date']
    fieldsets = (
        ('Thông tin cửa hàng', {
            'fields': (
                'user', 'store_name', 'image',
                'description', 'country', 'slug'
            )
        }),
        ('Thông tin hệ thống', {
            'fields': ('vendor_id', 'date'),
            'classes': ('collapse',)
        }),
    )


class PayoutAdmin(admin.ModelAdmin):
    list_display = ['payout_id', 'vendor', 'item', 'amount', 'date']
    search_fields = ['payout_id', 'vendor__store_name']
    list_filter = ['date', 'vendor']
    date_hierarchy = 'date'
    readonly_fields = ['payout_id', 'date']


class BankAccountAdmin(admin.ModelAdmin):
    list_display = [
        'vendor', 'bank_name', 
        'account_number', 'account_name',
        'account_type'
    ]
    search_fields = ['vendor__store_name', 'bank_name', 'account_number']
    list_filter = ['account_type']
    fieldsets = (
        ('Thông tin nhà bán hàng', {
            'fields': ('vendor', 'account_type')
        }),
        ('Thông tin ngân hàng', {
            'fields': (
                'bank_name', 'bank_code',
                'account_number', 'account_name'
            )
        }),
    )


class NotificationsAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'order', 'seen', 'date']
    list_editable = ['seen']
    list_filter = ['type', 'seen']
    search_fields = ['user__username']
    date_hierarchy = 'date'
    readonly_fields = ['date']


admin.site.register(vendor_models.Vendor, VendorAdmin)
admin.site.register(vendor_models.Payout, PayoutAdmin)
admin.site.register(vendor_models.BankAccount, BankAccountAdmin)
admin.site.register(vendor_models.Notifications, NotificationsAdmin)