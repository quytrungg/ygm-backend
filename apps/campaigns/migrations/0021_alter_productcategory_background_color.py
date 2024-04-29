# Generated by Django 4.2.5 on 2023-09-29 02:59

from django.db import migrations, models
from django.db.models import functions


def fix_product_category_background_color_data(apps, schema_editor) -> None:
    """Change product category's background color to hex color values."""
    ProductCategory = apps.get_model("campaigns", "ProductCategory")
    ProductCategory.objects.exclude(background_color="").update(
        background_color=functions.Concat(
            models.Value("#"), models.F("background_color"),
        ),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0020_alter_productcategory_options_productcategory_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcategory',
            name='background_color',
            field=models.CharField(blank=True, max_length=7, verbose_name='Background Color'),
        ),
        migrations.RunPython(
            fix_product_category_background_color_data,
            reverse_code=migrations.RunPython.noop,
        ),
    ]