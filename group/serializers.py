from rest_framework import serializers
from .models import Groups, Acceptances
from members.serializers import UserSerializer 
from bucketlist.serializers import BucketlistSerializer
class GroupSerializer(serializers.ModelSerializer):
    bid = BucketlistSerializer(read_only=True) 
    userid = UserSerializer(read_only=True)
    class Meta:
        model = Groups
        fields = ['userid','bid', 'muuid','name', 'members', 'created_at', 'updated_at']
        read_only_fields = ['userid', 'created_at', 'updated_at']

class AcceptanceSerializer(serializers.ModelSerializer):
    gid = GroupSerializer(read_only=True)
    class Meta:
        model = Acceptances
        fields = ['userid', 'gid']  # Include any other fields you need serialized
