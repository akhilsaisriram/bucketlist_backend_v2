from django.db import models
from members.models import CustomUser
from django.contrib.gis.db import models as gis_models

# Create your models here.
class Service(models.Model):
    userid = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='service')
    origin = models.CharField(max_length=255,null=True,blank=True)
    ocord = gis_models.PointField(srid=4326, blank=True, null=True)  # SRID 4326 for GPS coordinates (latitude/longitude)
    servicetype=models.CharField(blank=True,null=True,max_length=255)
    proofid=models.JSONField(blank=True,null=True,default=list)
    media=models.JSONField(blank=True,null=True,default=list)
    mediatype=models.JSONField(blank=True,null=True,default=list)
    likes=models.IntegerField(null=True,blank=True,default=0)
    comments=models.JSONField(null=True,blank=True,default=list)
    dislikes=models.IntegerField(null=True,blank=True,default=0)
    discription=models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    service_name = models.CharField(max_length=255, blank=True, null=True)
    available_days = models.JSONField(default=list, blank=True, null=True)
    start_time = models.TextField(blank=True, null=True)
    end_time = models.TextField(blank=True, null=True)
    
    # New contact number fields
    contact_number1 = models.CharField(max_length=15, blank=True, null=True)
    contact_number2 = models.CharField(max_length=15, blank=True, null=True)

   
