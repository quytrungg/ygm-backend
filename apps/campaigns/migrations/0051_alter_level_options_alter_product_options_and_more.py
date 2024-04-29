# Generated by Django 4.2.10 on 2024-03-07 02:27

from django.db import migrations, models


def populate_product_order_data(apps, schema_editor) -> None:
    """Populate product data with order field for each category."""
    Product = apps.get_model("campaigns", "Product")
    ProductCategory = apps.get_model("campaigns", "ProductCategory")
    products = Product.objects.all()
    updated_products = {
        product: idx
        for category_id in ProductCategory.objects.all().values_list(
            "id",
            flat=True,
        )
        for idx, product in enumerate(products.filter(category_id=category_id))
    }
    for product, idx in updated_products.items():
        product.order = idx
    Product.objects.bulk_update(
        updated_products.keys(),
        fields=["order"],
    )


def populate_level_order_data(apps, schema_editor) -> None:
    """Populate level data with order field for each product."""
    Level = apps.get_model("campaigns", "Level")
    Product = apps.get_model("campaigns", "Product")
    levels = Level.objects.all()
    updated_levels = {
        level: idx
        for product_id in Product.objects.all().values_list("id", flat=True)
        for idx, level in enumerate(levels.filter(product_id=product_id))
    }
    for level, idx in updated_levels.items():
        level.order = idx
    Level.objects.bulk_update(
        updated_levels.keys(),
        fields=["order"],
    )


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0050_campaign_external_chamber_id"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="level",
            options={
                "ordering": ("order",),
                "verbose_name": "Level",
                "verbose_name_plural": "Levels",
            },
        ),
        migrations.AlterModelOptions(
            name="product",
            options={
                "ordering": ("order",),
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
            },
        ),
        migrations.AddField(
            model_name="level",
            name="order",
            field=models.PositiveIntegerField(
                db_index=True, default=0, editable=False, verbose_name="order",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="product",
            name="order",
            field=models.PositiveIntegerField(
                db_index=True, default=0, editable=False, verbose_name="order",
            ),
            preserve_default=False,
        ),
        migrations.RunPython(
            populate_product_order_data,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.RunPython(
            populate_level_order_data,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
