# Generated by Django 4.2.2 on 2023-07-24 10:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('chambers', '0008_remove_chamber_website_chamber_subdomain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chamber',
            name='nickname',
            field=models.CharField(db_collation='case_insensitive', max_length=255, verbose_name='Nick Name'),
        ),
        migrations.AlterField(
            model_name='chamber',
            name='subdomain',
            field=models.CharField(max_length=63, null=True, verbose_name='Subdomain'),
        ),
        migrations.AddConstraint(
            model_name='chamber',
            constraint=models.UniqueConstraint(condition=models.Q(('deleted_at__isnull', True)), fields=('nickname',), name='chambers_unique_nickname'),
        ),
        migrations.AddConstraint(
            model_name='chamber',
            constraint=models.UniqueConstraint(condition=models.Q(('deleted_at__isnull', True)), fields=('subdomain',), name='chambers_unique_subdomain'),
        ),
    ]
