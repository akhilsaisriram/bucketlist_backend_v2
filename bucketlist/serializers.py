from rest_framework import serializers
from .models import Bucketlist
from members.serializers import UserSerializer
class BucketlistSerializer(serializers.ModelSerializer):
    uid = UserSerializer(read_only=True)
    class Meta:
        model = Bucketlist
        fields = ['uid','id','origin', 'destination', 'bucket', 'ocord', 'dcord', 'created_at', 'updated_at','start_date','end_date','visble']
        read_only_fields = ['uid', 'created_at', 'updated_at']

   
