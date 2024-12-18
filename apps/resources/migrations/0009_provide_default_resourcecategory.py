# Generated by Django 4.2.7 on 2024-01-19 08:30

from django.db import migrations, models
from apps.resources.constants import DEFAULT_RESOURCE_CATEGORIES


def provide_default_resource_categories(apps, schema_editor) -> None:
    """Provide default resource categories for each chamber."""
    Chamber = apps.get_model("chambers", "Chamber")
    ResourceCategory = apps.get_model("resources", "ResourceCategory")
    chamber_ids = Chamber.objects.values_list("id", flat=True)
    resource_categories = []
    for chamber_id in chamber_ids:
        resource_categories.extend(
            [
                ResourceCategory(
                    **resource_category_data,
                    chamber_id=chamber_id,
                ) for resource_category_data in DEFAULT_RESOURCE_CATEGORIES
            ],
        )
    ResourceCategory.objects.bulk_create(resource_categories)


def remove_default_resource_categories(apps, schema_editor) -> None:
    """Remove default resource categories in each chamber."""
    ResourceCategory = apps.get_model("resources", "ResourceCategory")
    ResourceCategory.objects.filter(
        name__in=[
            resource["name"] for resource in DEFAULT_RESOURCE_CATEGORIES
        ],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0008_resourcecategory_parent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resourcecategory',
            name='parent',
        ),
        migrations.RunPython(
            provide_default_resource_categories,
            reverse_code=remove_default_resource_categories,
        ),
    ]
