from django.urls import path

from apps.users.api.auth import views

urlpatterns = [
    path("login/", views.SuperAdminLoginView.as_view(), name="login"),
]
