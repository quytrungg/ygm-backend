# Generated by Django 4.2.2 on 2023-08-16 16:37

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
from django.utils.translation import gettext_lazy as _


def update_timeline_category_to_foreign_key(apps, schema_editor) -> None:
    """Move category in timeline data from char field to foreign key."""
    Timeline = apps.get_model("timelines", "Timeline")
    TimelineCategory = apps.get_model("timelines", "TimelineCategory")
    category_list = Timeline.objects.all().values_list("category", flat=True).distinct()
    category_map = {
        category: TimelineCategory(name=category)
        for category in category_list
    }
    TimelineCategory.objects.bulk_create(category_map.values())
    for timeline in Timeline.objects.all():
        timeline.category = str(category_map.get(timeline.category).id)
        timeline.save()


def revert_timeline_category_to_string(apps, schema_editor) -> None:
    """Revert back category in timeline data from foreign key to char field."""
    Timeline = apps.get_model("timelines", "Timeline")
    TimelineCategory = apps.get_model("timelines", "TimelineCategory")
    category_map = {
        str(category.pk): category.name
        for category in TimelineCategory.objects.all()
    }
    for timeline in Timeline.objects.all():
        timeline.category = category_map.get(timeline.category)
        timeline.save()


class Migration(migrations.Migration):

    dependencies = [
        ('timelines', '0002_timeline_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimelineCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('deleted_at', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Timeline Category',
                'verbose_name_plural': 'Timeline Categories',
            },
        ),
        migrations.RunPython(
            update_timeline_category_to_foreign_key,
            reverse_code=revert_timeline_category_to_string,
        ),
        migrations.AlterField(
            model_name='timeline',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timelines', to='timelines.timelinecategory', verbose_name='Category'),
        ),
    ]
