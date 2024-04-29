from django.urls import path

from knox import views as knox_views

from apps.users.api.auth import views

urlpatterns = [
    path("logout/", knox_views.LogoutView.as_view(), name="logout"),
    path(
        "logout-all/", knox_views.LogoutAllView.as_view(),
        name="logout_all",
    ),
    path(
        "password-reset/", views.PasswordResetView.as_view(),
        name="password-reset",
    ),
    path(
        "password-reset-confirm/", views.PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
