from django.contrib import admin
from blog import models as blog_models


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class BlogAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'category',
        'status', 'is_featured', 'views', 'date'
    ]
    list_editable = ['status', 'is_featured']
    search_fields = ['title', 'author__username', 'category__name']
    list_filter = ['status', 'is_featured', 'category']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'date'
    readonly_fields = ['views', 'date']
    fieldsets = (
        ('Thông tin bài viết', {
            'fields': (
                'title', 'slug', 'author',
                'category', 'image', 'content'
            )
        }),
        ('Cài đặt', {
            'fields': ('status', 'is_featured', 'tags')
        }),
        ('Thống kê', {
            'fields': ('views', 'likes', 'date'),
            'classes': ('collapse',)
        }),
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'blog', 'approved', 'date']
    list_editable = ['approved']
    search_fields = ['full_name', 'email', 'blog__title']
    list_filter = ['approved', 'date']
    date_hierarchy = 'date'
    readonly_fields = ['date']


admin.site.register(blog_models.Category, CategoryAdmin)
admin.site.register(blog_models.Blog, BlogAdmin)
admin.site.register(blog_models.Comment, CommentAdmin)