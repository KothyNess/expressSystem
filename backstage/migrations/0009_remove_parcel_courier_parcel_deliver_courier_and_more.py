# Generated by Django 4.1 on 2023-10-16 06:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backstage', '0008_statistics'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parcel',
            name='courier',
        ),
        migrations.AddField(
            model_name='parcel',
            name='deliver_courier',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='deliver_parcels', to='backstage.courier'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parcel',
            name='destination_station',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='destination_parcels', to='backstage.station'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parcel',
            name='get_company',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='get_company_parcels', to='backstage.branchoffice'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parcel',
            name='get_courier',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='get_parcels', to='backstage.courier'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parcel',
            name='get_station',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='get_station_parcels', to='backstage.station'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='parcel',
            name='destination_branch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination_parcels', to='backstage.branchoffice'),
        ),
        migrations.AlterField(
            model_name='parcel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_parcels', to='backstage.user'),
        ),
    ]
