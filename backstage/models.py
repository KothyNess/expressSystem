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

class User(models.Model):
    username = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)


class Parcel(models.Model):
    timestamp = models.DateTimeField(primary_key=True, default=timezone.now)
    destination = models.CharField(max_length=255)
    destination_branch = models.ForeignKey(BranchOffice, on_delete=models.CASCADE)
    weight = models.FloatField()
    recipient = models.CharField(max_length=255)
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.timestamp:
            self.timestamp = timezone.now()
        super().save(*args, **kwargs)

    @property
    def timestamp_in_milliseconds(self):
        return int(self.timestamp.timestamp() * 1000)

class Shipment(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.CASCADE)
    status = models.CharField(max_length=255)

class Admin(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    admin_name = models.CharField(max_length=255)