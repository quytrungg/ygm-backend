# Generated by Django 4.2.2 on 2023-07-10 09:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('campaigns', '0005_alter_productattachment_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='goal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Team Goal'),
        ),
        migrations.AlterField(
            model_name='usercampaign',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='members', to='campaigns.team', verbose_name='Team'),
        ),
    ]