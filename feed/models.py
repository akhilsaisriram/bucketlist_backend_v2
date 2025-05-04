from django.db import models
from members.models import CustomUser
from django.contrib.gis.db import models as gis_models

# Create your models here.
class Feed(models.Model):
    userid = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feedusers')
    origin = models.CharField(max_length=255)
    ocord = gis_models.PointField(srid=4326, blank=True, null=True)  # SRID 4326 for GPS coordinates (latitude/longitude)
    media=models.TextField(blank=True,null=True)
    mediatype=models.CharField(max_length=255,blank=True,null=True)
    likes=models.IntegerField(null=True,blank=True,default=0)
    liked_by = models.JSONField(default=list)  # List of user IDs who liked the feed
    disliked_by = models.JSONField(default=list)
    comments=models.JSONField(null=True,blank=True,default=list)
    dislikes=models.IntegerField(null=True,blank=True,default=0)
    content=models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    typeofcontent=models.CharField(max_length=100,default="None")

   
