from django import forms
from django.contrib import admin

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import ProductCategory


class ProductCategoryForm(forms.ModelForm):
    """ProductCategory's form in django admin."""

    class Meta:
        model = ProductCategory
        fields = "__all__"
        widgets = {
            "campaign": autocomplete.ModelSelect2(url="campaign-autocomplete"),
        }


@admin.register(ProductCategory)
class ProductCategoryAdmin(BaseAdmin):
    """Admin UI for ProductCategory model."""

    ordering = (
        "name",
    )

    list_display = (
        "id",
        "name",
        "order",
        "campaign",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = ("name",)
    readonly_fields = BaseAdmin.readonly_fields + ("external_id",)
    form = ProductCategoryForm
