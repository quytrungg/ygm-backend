from django.db import migrations, models
from ..constants import TimelineCategoryNames


def migrate_timeline_categories(apps, schema_editor):
    """Delete current data and migrate new data for timeline categories."""
    TimelineCategory = apps.get_model("timelines", "TimelineCategory")
    TimelineCategory.objects.all().delete()
    timeline_categories = [
        TimelineCategory(name=name) for name in TimelineCategoryNames
    ]
    TimelineCategory.objects.bulk_create(timeline_categories)


class Migration(migrations.Migration):
    dependencies = [
        ("timelines", "0006_alter_timeline_assigned_to"),
    ]

    operations = [
        migrations.RunPython(
            migrate_timeline_categories,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
