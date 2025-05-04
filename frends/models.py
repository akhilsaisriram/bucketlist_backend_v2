from django.db import models
from members.models import CustomUser

# Create your models here.
class Frends(models.Model):
    userid = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='frends')
    following = models.JSONField(null=True,blank=True,default=list)  
    followers=models.JSONField(null=True,blank=True,default=list)
    posts=models.JSONField(null=True,blank=True,default=list)
    settings=models.JSONField(null=True,blank=True,default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

   
