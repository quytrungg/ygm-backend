from django.urls import path

from drf_spectacular import views

app_name = "open_api"

# OpenApi urls
urlpatterns = [
    path(
        route="schema/",
        view=views.SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        route="ui/",
        view=views.SpectacularSwaggerView.as_view(
            url_name="open_api:schema",
        ),
        name="ui",
    ),
]
