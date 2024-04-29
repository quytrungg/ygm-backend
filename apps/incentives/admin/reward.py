from django import forms
from django.contrib import admin

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import Reward


class RewardForm(forms.ModelForm):
    """Reward's form in django admin."""

    class Meta:
        model = Reward
        fields = "__all__"
        widgets = {
            "incentive": autocomplete.ModelSelect2(
                url="incentive-autocomplete",
            ),
            "user_campaign": autocomplete.ModelSelect2(
                url="user-campaign-autocomplete",
            ),
        }


@admin.register(Reward)
class RewardAdmin(BaseAdmin):
    """Admin UI for Reward model."""

    list_display = (
        "id",
        "incentive",
        "user_campaign",
        "paid_at",
    )
    search_fields = (
        "incentive__name",
        "user_campaign__first_name",
        "user_campaign__last_name",
    )
    form = RewardForm

    def has_add_permission(self, request):
        """Don't allow adding through django admin."""
        return False
