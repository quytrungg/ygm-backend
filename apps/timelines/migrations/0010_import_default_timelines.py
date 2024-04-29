import csv

from django.db import migrations
from django.db.models import OuterRef, Subquery

from apps.timelines.constants import TimelineTypeChoice
from apps.users.constants import UserRole


def import_default_timelines(apps, schema_editor) -> None:
    """Import default timelines into db system."""
    User = apps.get_model("users", "User")
    Chamber = apps.get_model("chambers", "Chamber")
    Timeline = apps.get_model("timelines", "Timeline")
    TimelineCategory = apps.get_model("timelines", "TimelineCategory")
    chamber_created_by_info = Chamber.objects.annotate(
        ca_id=Subquery(
            User.objects.filter(
                role=UserRole.CHAMBER_ADMIN,
                chamber=OuterRef("pk"),
            ).values("id")[:1],
        ),
        order=Subquery(
            Timeline.objects.filter(
                chamber=OuterRef("pk"),
            ).order_by("order").values("order")[:1],
        ),
    ).filter(ca_id__isnull=False).values_list("id", "ca_id", "order")
    imported_timelines = []
    category_map = dict(TimelineCategory.objects.values_list("name", "id"))
    with open(
        "assets/timelines/23OS Timeline TC sample.xlsx - Sheet1.csv",
        encoding="utf-8",
    ) as tc_file:
        csv_reader = csv.reader(tc_file, delimiter=",")
        # skip the header
        next(csv_reader)
        tc_data = list(csv_reader)
        for chamber_id, created_by_id, order in chamber_created_by_info:
            order = order or 0
            imported_timelines.extend(
                [
                    Timeline(
                        category_id=category_map.get(row[0]),
                        name=row[1],
                        assigned_to=row[2],
                        description=row[3],
                        chamber_id=chamber_id,
                        created_by_id=created_by_id,
                        type=TimelineTypeChoice.WITHOUT_VICE_CHAIR,
                        order=order+index,
                    ) for index, row in enumerate(tc_data)
                ],
            )
    with open(
        "assets/timelines/23OS Timeline VC sample.xlsx - Sheet1.csv",
        encoding="utf-8",
    ) as vc_file:
        csv_reader = csv.reader(vc_file, delimiter=",")
        next(csv_reader)
        vc_data = list(csv_reader)
        for chamber_id, created_by_id, order in chamber_created_by_info:
            order = order or 0
            imported_timelines.extend(
                [
                    Timeline(
                        category_id=category_map.get(row[0]),
                        name=row[1],
                        assigned_to=row[2],
                        description=row[3],
                        chamber_id=chamber_id,
                        created_by_id=created_by_id,
                        type=TimelineTypeChoice.WITH_VICE_CHAIR,
                        order=order+index,
                    ) for index, row in enumerate(vc_data)
                ],
            )
    Timeline.objects.bulk_create(imported_timelines)


def remove_imported_timelines(apps, schema_editor) -> None:
    """Remove imported timelines."""
    Timeline = apps.get_model("timelines", "Timeline")
    Timeline.objects.exclude(type="").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_deleted_at_user_deleted_by_cascade'),
        ('timelines', '0009_timeline_type_alter_timeline_due_date'),
    ]

    operations = [
        migrations.RunPython(
            import_default_timelines,
            reverse_code=remove_imported_timelines,
        ),
    ]
