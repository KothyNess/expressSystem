# Generated by Django 4.1 on 2023-10-17 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backstage', '0013_alter_parcel_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='info',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
