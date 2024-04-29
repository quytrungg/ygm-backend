from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _

from dal import autocomplete
from imagekit.admin import AdminThumbnail

from ..core.admin import BaseAdmin
from .models import User


class UserForm(UserChangeForm):
    """User's form in django admin."""

    class Meta(UserChangeForm.Meta):
        widgets = {
            "chamber": autocomplete.ModelSelect2(url="chamber-autocomplete"),
        }


@admin.register(User)
class UserAdmin(BaseAdmin, DjangoUserAdmin):
    """UI for User model."""

    ordering = ("email",)
    avatar_thumbnail = AdminThumbnail(image_field="avatar_thumbnail")
    list_display = (
        "avatar_thumbnail",
        "email",
        "first_name",
        "last_name",
        "chamber",
        "is_staff",
        "is_superuser",
    )
    list_display_links = (
        "email",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
    )
    add_fieldsets = (
        (
            None, {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    form = UserForm
    fieldsets = (
        (
            None, {
                "fields": (
                    "email",
                    "password",
                ),
            },
        ),
        (
            _("Personal info"), {
                "fields": (
                    "first_name",
                    "last_name",
                    "avatar",
                    "chamber",
                    "role",
                ),
            },
        ),
        (
            _("Permissions"), {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
