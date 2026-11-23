from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.i18n import t

admin.site.site_header = t("admin_site_header")
admin.site.site_title = t("admin_site_title")
admin.site.index_title = t("admin_index_title")

urlpatterns = [
    # The admin path is read from the DJANGO_ADMIN_PATH setting
    path(settings.ADMIN_PATH, admin.site.urls),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.page_not_found"
handler500 = "core.views.server_error"
