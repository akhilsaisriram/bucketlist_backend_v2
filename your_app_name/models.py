from django.contrib.gis.db import models

class Locationa(models.Model):
    name = models.CharField(max_length=100)
    coordinates = models.PointField()  # GeoDjango PointField for storing lat/lon

    def __str__(self):
        return self.name
