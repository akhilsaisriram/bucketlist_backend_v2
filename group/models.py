from django.db import models
from bucketlist.models import Bucketlist
from django.contrib.gis.db import models as gis_models
import uuid
from members.models import CustomUser

class Groups(models.Model):
    userid = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mem_group')  # Changed related_name
    bid = models.ForeignKey(Bucketlist, on_delete=models.CASCADE, related_name='bid')
    muuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    members = models.JSONField(null=True, blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Acceptances(models.Model):
    userid = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mem_group_accept')  # Changed related_name
    gid = models.ForeignKey(Groups, on_delete=models.CASCADE, related_name='groupid')

