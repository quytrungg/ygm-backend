# Generated by Django 4.2.5 on 2023-10-17 02:51

from django.db import migrations

from apps.campaigns.constants import NoteType


def populate_missing_notes_for_campaigns(apps, schema_editor):
    """Create notes for campaign as they were not created."""
    Note = apps.get_model('campaigns', 'Note')
    Campaign = apps.get_model('campaigns', 'Campaign')

    for campaign in Campaign.objects.filter(notes__isnull=True):
        notes = [
            Note(
                type=note_type.value,
                campaign=campaign,
                body="",
            ) for note_type in NoteType
        ]
        Note.objects.bulk_create(notes)


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0026_note_modified_by_alter_note_created_by'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='note',
            options={'verbose_name': 'Note', 'verbose_name_plural': 'Notes'},
        ),
        migrations.AlterUniqueTogether(
            name='note',
            unique_together={('campaign', 'type')},
        ),
        migrations.RemoveField(
            model_name='note',
            name='name',
        ),
        migrations.RunPython(
            populate_missing_notes_for_campaigns,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
