from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import Member


class MemberForm(forms.ModelForm):
    """Member's form in django admin."""

    class Meta:
        model = Member
        fields = "__all__"
        widgets = {
            "stored_member": autocomplete.ModelSelect2(
                url="stored-member-autocomplete",
            ),
        }


@admin.register(Member)
class MemberAdmin(BaseAdmin):
    """Admin UI for Member model."""

    ordering = (
        "name",
    )
    list_display = (
        "id",
        "name",
        "title",
        "email",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = (
        "name",
    )
    form = MemberForm
    fieldsets = (
        (
            _("Business info"), {
                "fields": (
                    "stored_member",
                    "name",
                    "title",
                    "email",
                ),
            },
        ),
        (
            _("Address"), {
                "fields": (
                    "address",
                    "city",
                    "state",
                    "zipcode",
                    "country",
                ),
            },
        ),
        (
            _("Contact"), {
                "fields": (
                    "phone",
                    "fax",
                    "contact_methods",
                ),
            },
        ),
    )
