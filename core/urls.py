from django.urls import include, path

urlpatterns = [
    path(
        "api/",
        include(
            [
                path(
                    "v1/",
                    include(
                        [
                            path("accounts/", include("accounts.urls")),
                            path("admin/", include("medwb_admins.urls")),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
