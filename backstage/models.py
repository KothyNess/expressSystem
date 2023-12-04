from django.db import models
from django.utils import timezone


class BranchOffice(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)


class Station(models.Model):
    name = models.CharField(max_length=255)
    branch_office = models.ForeignKey(BranchOffice, on_delete=models.CASCADE)


class Courier(models.Model):
    name = models.CharField(max_length=255)
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)


class User(models.Model):
    username = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)


class Parcel(models.Model):
    timestamp = models.BigIntegerField(primary_key=True)
    object_name = models.CharField(max_length=255)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient')
    weight = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_parcels')
    destination_branch = models.ForeignKey(BranchOffice, on_delete=models.CASCADE, related_name='destination_parcels')
    destination_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='destination_parcels')
    deliver_courier = models.ForeignKey(Courier, on_delete=models.CASCADE, related_name='deliver_parcels')
    get_station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='get_station_parcels')
    get_company = models.ForeignKey(BranchOffice, on_delete=models.CASCADE, related_name='get_company_parcels')
    get_courier = models.ForeignKey(Courier, on_delete=models.CASCADE, related_name='get_parcels')
    Price = models.FloatField()

    def save(self, *args, **kwargs):
        if not self.timestamp:
            self.timestamp = int(timezone.now().timestamp())
        super(Parcel, self).save(*args, **kwargs)

    @property
    def timestamp_in_milliseconds(self):
        return self.timestamp * 1000  # 因为我们现在存储的是以秒为单位的时间戳，所以乘以1000得到毫秒


class Shipment(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)
    info = models.CharField(max_length=255)

class Admin(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    admin_name = models.CharField(max_length=255)


class Statistics(models.Model):
    date = models.DateField()
    branch_office = models.ForeignKey(BranchOffice, on_delete=models.CASCADE, null=True, blank=True)
    station = models.ForeignKey(Station, on_delete=models.CASCADE, null=True, blank=True)
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, null=True, blank=True)

    pickup_count = models.IntegerField(default=0)  # 揽件统计
    dispatch_count = models.IntegerField(default=0)  # 发件统计
    delivery_count = models.IntegerField(default=0)  # 送件统计

    class Meta:
        verbose_name = "Statistic"
        verbose_name_plural = "Statistics"
        unique_together = (('date', 'branch_office', 'station', 'courier'),)  # 唯一约束，确保每个组合只有一个统计记录

    def __str__(self):
        return f"Statistics for {self.date}"
