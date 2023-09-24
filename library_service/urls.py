from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("doc/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("user/", include("user.urls")),
    path("library/", include("library.urls")),
    path("borrowing/", include("borrowing.urls")),
    path("payments/", include("payment.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
