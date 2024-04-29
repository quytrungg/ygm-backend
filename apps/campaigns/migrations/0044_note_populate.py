# Generated by Django 4.2.7 on 2024-01-30 03:22

from django.db import migrations, models

from apps.campaigns.constants import NoteType
from apps.campaigns.context_managers import get_context_manager


def populate_notes(apps, schema_editor):
    """Generate notes for all existing campaigns."""
    Campaign = apps.get_model("campaigns", "Campaign")
    Note = apps.get_model("campaigns", "Note")
    notes = []
    for campaign in Campaign.objects.annotate(
        note_conunt=models.Count("notes"),
    ).filter(note_conunt=0):
        notes.extend([
            Note(
                type=note_type.value,
                campaign=campaign,
                body=get_context_manager(note_type).get_default_template(),
            ) for note_type in NoteType
        ])
    Note.objects.bulk_create(notes)


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0043_merge_20240130_0317"),
    ]

    operations = [
        migrations.RunPython(populate_notes, migrations.RunPython.noop),
    ]
