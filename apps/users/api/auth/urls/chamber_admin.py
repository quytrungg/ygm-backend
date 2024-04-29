from django.urls import path

from apps.users.api.auth import views

urlpatterns = [
    path("login/", views.ChamberAdminLoginView.as_view(), name="login"),
    path(
        "register/",
        views.ChamberAdminRegisterAPIView.as_view(),
        name="register",
    ),
    path(
        "register_info/",
        views.ChamberAdminRegisterInfoAPIView.as_view(),
        name="register-info",
    ),
]
