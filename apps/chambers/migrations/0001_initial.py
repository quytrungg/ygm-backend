# Generated by Django 4.2.2 on 2023-06-13 08:28

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chamber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('nickname', models.CharField(max_length=255, verbose_name='Nick Name')),
                ('website', models.CharField(max_length=255, null=True, unique=True, verbose_name='Website')),
                ('address', models.CharField(blank=True, max_length=255, verbose_name='Address')),
                ('city', models.CharField(blank=True, max_length=50, verbose_name='City')),
                ('state', models.CharField(blank=True, max_length=2, verbose_name='State')),
                ('zipcode', models.CharField(blank=True, max_length=5, verbose_name='Zipcode')),
                ('country', models.CharField(blank=True, max_length=255, verbose_name='Country')),
                ('mail_address', models.EmailField(blank=True, max_length=254, verbose_name='Mail Address')),
                ('mail_city', models.CharField(blank=True, max_length=50, verbose_name='Mail City')),
                ('mail_state', models.CharField(blank=True, max_length=2, verbose_name='Mail State')),
                ('mail_zipcode', models.CharField(blank=True, max_length=5, verbose_name='Mail Zipcode')),
                ('mail_country', models.CharField(blank=True, max_length=255, verbose_name='Mail Country')),
                ('phone', models.CharField(blank=True, max_length=15, verbose_name='Phone')),
                ('member_count', models.IntegerField(default=0, verbose_name='Number of members')),
                ('city_population', models.IntegerField(default=0, verbose_name="City's population")),
                ('country_population', models.IntegerField(default=0, verbose_name="Country's population")),
                ('msa_population', models.IntegerField(default=0, verbose_name="MSA's population")),
                ('total_budget', models.DecimalField(decimal_places=3, default=Decimal('0'), max_digits=13, verbose_name='Total budget')),
                ('total_membership_budget', models.DecimalField(decimal_places=3, default=Decimal('0'), max_digits=13, verbose_name='Total membership budget')),
                ('pre_income', models.DecimalField(decimal_places=3, default=Decimal('0'), max_digits=13, verbose_name='Pre-TRC sponsorship income')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('trc_coord_name', models.CharField(blank=True, max_length=255, verbose_name='TRC Coord name')),
                ('trc_coord_email', models.EmailField(max_length=254, verbose_name='TRC Coord Email')),
                ('trc_coord_phone', models.CharField(blank=True, max_length=15, verbose_name='TRC Coord Phone')),
                ('trc_coord_title', models.CharField(blank=True, max_length=255, verbose_name='TRC Coord Title')),
                ('trc_coord_office_phone', models.CharField(blank=True, max_length=15, verbose_name='TRC Coord Office Phone')),
                ('trc_coord_office_phone_ext', models.CharField(blank=True, max_length=10, verbose_name='TRC Coord Office Phone ext')),
                ('ceo_name', models.CharField(blank=True, max_length=255, verbose_name='CEO Name')),
                ('ceo_email', models.EmailField(blank=True, max_length=254, verbose_name='CEO Email')),
                ('ceo_phone', models.CharField(blank=True, max_length=15, verbose_name='CEO Phone')),
                ('instagram_url', models.URLField(blank=True, max_length=255, verbose_name='Instagram URL')),
                ('facebook_url', models.URLField(blank=True, max_length=255, verbose_name='Facebook URL')),
                ('twitter_url', models.URLField(blank=True, max_length=255, verbose_name='Twitter URL')),
                ('youtube_url', models.URLField(blank=True, max_length=255, verbose_name='Youtube URL')),
                ('linkedin_url', models.URLField(blank=True, max_length=255, verbose_name='LinkedIn URL')),
            ],
            options={
                'verbose_name': 'Chamber',
                'verbose_name_plural': 'Chambers',
            },
        ),
        migrations.CreateModel(
            name='ChamberBranding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('site_primary_color', models.CharField(max_length=7, verbose_name="Site's default primary color")),
                ('site_secondary_color', models.CharField(max_length=7, verbose_name="Site's default secondary color")),
                ('site_alternate_color', models.CharField(max_length=7, verbose_name="Site's default alternate color")),
                ('chamber_logo', models.FileField(max_length=512, upload_to='', verbose_name='Chamber Logo')),
                ('trc_logo', models.FileField(max_length=512, upload_to='', verbose_name='Chamber Logo')),
                ('landing_bg', models.FileField(max_length=512, upload_to='', verbose_name='Landing background image')),
                ('headline', models.CharField(max_length=50, verbose_name='Headline')),
                ('public_prelaunch_msg', models.TextField(verbose_name='Public pre-launch message')),
                ('volunteer_prelaunch_msg', models.TextField(verbose_name='Volunteer pre-launch message')),
                ('chamber', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brandings', to='chambers.chamber', verbose_name='Chamber')),
            ],
            options={
                'verbose_name': 'Branding',
                'verbose_name_plural': 'Brandings',
            },
        ),
    ]