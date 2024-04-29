from django import forms
from django.contrib import admin

from dal import autocomplete

from apps.core.admin import BaseAdmin

from ..models import Product, ProductAttachment


class ProductAttachmentAdmin(admin.TabularInline):
    """Inline admin UI for ProductAttachment model."""

    model = ProductAttachment


class ProductForm(forms.ModelForm):
    """Product's form in django admin."""

    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "category": autocomplete.ModelSelect2(
                url="product-category-autocomplete",
            ),
        }


@admin.register(Product)
class ProductAdmin(BaseAdmin):
    """Admin UI for Product model."""

    ordering = (
        "name",
    )

    list_display = (
        "id",
        "name",
        "pre_trc_income",
        "category",
        "is_included_in_renewal",
    )
    list_display_links = (
        "id",
        "name",
    )
    search_fields = ("name",)
    readonly_fields = BaseAdmin.readonly_fields + ("external_id",)
    inlines = (ProductAttachmentAdmin,)
    form = ProductForm
