# Generated by Django 4.1 on 2023-10-16 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backstage', '0007_parcel_object_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('pickup_count', models.IntegerField(default=0)),
                ('dispatch_count', models.IntegerField(default=0)),
                ('delivery_count', models.IntegerField(default=0)),
                ('branch_office', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backstage.branchoffice')),
                ('courier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backstage.courier')),
                ('station', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backstage.station')),
            ],
            options={
                'verbose_name': 'Statistic',
                'verbose_name_plural': 'Statistics',
                'unique_together': {('date', 'branch_office', 'station', 'courier')},
            },
        ),
    ]