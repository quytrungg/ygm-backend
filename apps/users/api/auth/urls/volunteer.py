from django.urls import path

from apps.users.api.auth import views

urlpatterns = [
    path("login/", views.VolunteerLoginView.as_view(), name="login"),
    path(
        "register/",
        views.VolunteerRegisterAPIView.as_view(),
        name="register",
    ),
    path(
        "register-info/",
        views.VolunteerRegisterInfoAPIView.as_view(),
        name="register-info",
    ),
]
