# Generated by Django 4.2.7 on 2024-01-26 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timelines', '0008_alter_timeline_assigned_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeline',
            name='type',
            field=models.CharField(blank=True, choices=[('23os_tc', '23OS TC'), ('23os_vc', '23OS VC')], max_length=20, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='timeline',
            name='due_date',
            field=models.DateTimeField(null=True, verbose_name='Due Date'),
        ),
    ]