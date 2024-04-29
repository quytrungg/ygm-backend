from django import forms
from django.contrib import admin

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import UserCampaign


class UserCampaignForm(forms.ModelForm):
    """Team's form in django admin."""

    class Meta:
        model = UserCampaign
        fields = "__all__"
        widgets = {
            "campaign": autocomplete.ModelSelect2(url="campaign-autocomplete"),
            "user": autocomplete.ModelSelect2(url="user-autocomplete"),
            "team": autocomplete.ModelSelect2(url="team-autocomplete"),
            "member": autocomplete.ModelSelect2(
                url="stored-member-autocomplete",
            ),
        }


@admin.register(UserCampaign)
class UserCampaignAdmin(BaseAdmin):
    """Admin ui for UserCampaign model."""

    ordering = (
        "user",
    )

    list_display = (
        "id",
        "full_name",
        "email",
        "campaign",
    )
    search_fields = (
        "first_name",
        "last_name",
        "email",
    )
    form = UserCampaignForm
