from rest_framework import serializers
from .models import Frends

class FrendSerializer(serializers.ModelSerializer):

    class Meta:
        model = Frends
        fields = ['settings',  'posts', 'followers','following' ,'created_at', 'updated_at']
        read_only_fields = ['userid', 'created_at', 'updated_at']

   
