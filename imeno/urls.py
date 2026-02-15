from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# تنظیمات هدر پنل مدیریت
admin.site.site_header = "پنل مدیریت بیمه ایمنو"
admin.site.site_title = "ایمنو"
admin.site.index_title = "به پنل مدیریت خوش آمدید"

urlpatterns = [
    path('admin/', admin.site.urls),
    # نکته: وقتی include('core.urls') داری، دیگه نیازی به تعریف جداگانه path('', home) اینجا نیست
    # چون احتمالا داخل core.urls تعریفش کردی.
    path('', include('core.urls')), 
]

# نمایش تصاویر در حالت توسعه (Debug Mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)