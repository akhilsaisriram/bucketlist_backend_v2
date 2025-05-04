from django.db import models
from members.models import CustomUser
from django.contrib.gis.db import models as gis_models

# Create your models here.
class Bucketlist(models.Model):
    uid = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='members')
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    bucket = models.CharField(max_length=255)
    ocord = gis_models.PointField(srid=4326, blank=True, null=True)  # SRID 4326 for GPS coordinates (latitude/longitude)
    dcord = gis_models.PointField(srid=4326, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)  # Start date for the bucket list item
    end_date = models.DateTimeField(blank=True, null=True)    # End date for the bucket list item
    visble=models.IntegerField(blank=True,null=True,default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.bucket} from {self.origin} to {self.destination}"
