# Generated by Django 4.1 on 2023-10-12 10:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('backstage', '0002_alter_parcel_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parcel',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, primary_key=True, serialize=False),
        ),
    ]
