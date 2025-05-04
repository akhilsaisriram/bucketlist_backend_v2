# from rest_framework import serializers
# from .models import Service

# class serviceSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Service
#         fields = ['origin',  
#             'ocord', 
#             'servicetype',
#             'proofid',
#             'media',
#             'mediatype', 
#             'likes', 
#             'comments', 
#             'dislikes', 
#             'discription', 
#             'created_at', 
#             'updated_at']
#         read_only_fields = ['userid', 'created_at', 'updated_at']

from rest_framework import serializers
from .models import Service
from django.contrib.gis.geos import Point

class serviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id', 'userid', 'origin', 'ocord', 'servicetype', 
            'proofid', 'media', 'mediatype', 'likes', 'comments', 
            'dislikes', 'discription', 'created_at', 'updated_at',
            'service_name', 'available_days', 'start_time', 'end_time',
            'contact_number1', 'contact_number2'
        ]
        read_only_fields = ['userid', 'created_at', 'updated_at', 'likes', 'dislikes', 'comments']

    def create(self, validated_data):
        # Handle Point field for coordinates if present in the data
        if 'ocord' in validated_data and validated_data['ocord']:
            coords = validated_data['ocord']
            validated_data['ocord'] = Point(coords[0], coords[1], srid=4326)
        return super().create(validated_data)
