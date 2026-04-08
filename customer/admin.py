from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from customer import models as customer_models


class AddressAdmin(ImportExportModelAdmin):
    list_display = [
        'user', 'full_name', 'mobile',
        'city', 'state', 'country'
    ]
    search_fields = [
        'user__username', 'full_name',
        'mobile', 'city', 'state'
    ]
    list_filter = ['country', 'state']
    fieldsets = (
        ('Thông tin khách hàng', {
            'fields': ('user', 'full_name', 'mobile', 'email')
        }),
        ('Địa chỉ', {
            'fields': (
                'address', 'city', 
                'state', 'country', 'zip_code'
            )
        }),
    )


class WishlistAdmin(ImportExportModelAdmin):
    list_display = ['user', 'product']
    search_fields = ['user__username', 'product__name']
    list_filter = ['product__category']


class NotificationAdmin(ImportExportModelAdmin):
    list_display = ['user', 'type', 'seen', 'date']
    list_editable = ['seen']
    list_filter = ['type', 'seen']
    search_fields = ['user__username']
    date_hierarchy = 'date'
    readonly_fields = ['date']


admin.site.register(customer_models.Address, AddressAdmin)
admin.site.register(customer_models.Wishlist, WishlistAdmin)
admin.site.register(customer_models.Notifications, NotificationAdmin)