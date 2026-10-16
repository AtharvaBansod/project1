from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "IndustroLink Administration"
admin.site.site_title = "IndustroLink Admin"
admin.site.index_title = "Catalog, enquiries and service management"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("products/", include("catalog.urls")),
    path("enquiry/", include("enquiries.urls")),
    path("services/", include("services.urls")),
    path("manage/", include("manager.urls")),
    path("", include("core.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
