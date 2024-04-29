# Generated by Django 4.2.2 on 2023-07-20 02:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('campaigns', '0008_alter_usercampaign_role'),
        ('chambers', '0007_alter_chamber_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='name',
            field=models.CharField(db_collation='case_insensitive', max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='status',
            field=models.CharField(choices=[('created', 'Campaign Created'), ('open', 'Open Renewal'), ('live', 'Go Live'), ('done', 'Mark As Done')], default='created', max_length=20, verbose_name='Status'),
        ),
    ]
