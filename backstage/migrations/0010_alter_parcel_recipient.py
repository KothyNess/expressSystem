# Generated by Django 4.1 on 2023-10-16 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backstage', '0009_remove_parcel_courier_parcel_deliver_courier_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parcel',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipient', to='backstage.user'),
        ),
    ]
