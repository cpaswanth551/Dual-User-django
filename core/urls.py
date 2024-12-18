from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path(
        "api/",
        include(
            [
                path(
                    "v1/",
                    include(
                        [
                            path("admin/", include("medwb_admins.urls")),
                            path("accounts/", include("accounts.urls")),
                        ]
                    ),
                ),
            ]
        ),
    ),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
