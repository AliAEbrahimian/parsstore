from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "مدیریت پارس تکستایل"
admin.site.site_title = "پارس تکستایل"
admin.site.index_title = "پنل مدیریت سایت"

urlpatterns = [
    # مسیر پنل مدیریت از متغیر DJANGO_ADMIN_PATH خوانده می‌شود
    path(settings.ADMIN_PATH, admin.site.urls),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.page_not_found"
handler500 = "core.views.server_error"
