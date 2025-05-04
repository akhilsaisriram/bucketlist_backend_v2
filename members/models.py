# from django.contrib.auth.models import AbstractUser
# from django.db import models
# import uuid

# class CustomUser(AbstractUser):
  

#     phone = models.CharField(max_length=15, blank=True, null=True)
#     dob = models.DateField(blank=True, null=True)

#     # Override groups and user_permissions fields
#     groups = models.ManyToManyField(
#         'auth.Group',
#         related_name='customuser_set',  # Change this line
#         blank=True,
#     )
#     user_permissions = models.ManyToManyField(
#         'auth.Permission',
#         related_name='customuser_set',  # Change this line
#         blank=True,
#     )




from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model extending the default Django User.
    """
    phone = models.CharField(max_length=15, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)

    # New fields
    place = models.CharField(max_length=255, blank=True, null=True)  # Stores the place name
    ocord = gis_models.PointField(srid=4326, blank=True, null=True)  # GPS coordinates (longitude/latitude)

    # Override groups and user_permissions fields
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  # Change related_name for CustomUser
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  # Change related_name for CustomUser
        blank=True,
    )

    def __str__(self):
        return self.username
