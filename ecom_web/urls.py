from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# Bỏ auth_views ở đây vì password reset đã được xử lý trong userauths/urls.py
from userauths import views as userauths_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("store.urls")),
    path('auth/', include("userauths.urls")),  # password reset nằm trong này rồi
    # path('customer/', include("customer.urls")),
    # path('vendor/', include("vendor.urls")),
    # path('blog/', include("blog.urls")),

    path("ckeditor5/", include('django_ckeditor_5.urls')),

    # Handler lỗi
    path('404/', userauths_views.handler404, name='404'),
    path('500/', userauths_views.handler500, name='500'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Handler lỗi toàn cục
handler404 = 'userauths.views.handler404'
handler500 = 'userauths.views.handler500'