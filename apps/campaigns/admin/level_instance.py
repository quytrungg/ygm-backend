from django import forms
from django.contrib import admin

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import LevelInstance


class LevelInstanceForm(forms.ModelForm):
    """LevelInstance's form in django admin."""

    class Meta:
        model = LevelInstance
        fields = "__all__"
        widgets = {
            "level": autocomplete.ModelSelect2(url="level-autocomplete"),
            "contract": autocomplete.ModelSelect2(url="contract-autocomplete"),
        }


@admin.register(LevelInstance)
class LevelInstanceAdmin(BaseAdmin):
    """Admin UI for LevelInstance model."""

    list_display = (
        "id",
        "level",
        "contract",
        "cost",
        "declined_at",
    )
    list_display_links = (
        "id",
        "level",
        "contract",
    )
    search_fields = (
        "level__name",
        "contract__name",
    )
    create_only_fields = (
        "level",
        "contract",
    )
    form = LevelInstanceForm
    fieldsets = (
        (
            None, {
                "fields": (
                    "level",
                    "contract",
                    "cost",
                    "declined_at",
                ),
            },
        ),
    )
