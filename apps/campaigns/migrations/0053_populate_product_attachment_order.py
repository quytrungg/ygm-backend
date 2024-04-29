from django.db import migrations, models


def populate_product_attachment_data(apps, schema_editor) -> None:
    """Populate product attachment order within each product."""
    Product = apps.get_model("campaigns", "Product")
    ProductAttachment = apps.get_model("campaigns", "ProductAttachment")
    product_attachments = ProductAttachment.objects.all()
    updated_product_attachments = {
        attachment: idx
        for product_id in Product.objects.values_list("id", flat=True)
        for idx, attachment in enumerate(
            product_attachments.filter(product_id=product_id),
        )
    }
    for attachment, idx in updated_product_attachments.items():
        attachment.order = idx
    ProductAttachment.objects.bulk_update(
        updated_product_attachments.keys(),
        fields=["order"],
    )


class Migration(migrations.Migration):
    """Populate product attachment order within each product."""

    dependencies = [
        ("campaigns", "0052_alter_productattachment_options_and_more"),
    ]
    operations = [
        migrations.RunPython(
            code=populate_product_attachment_data,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
