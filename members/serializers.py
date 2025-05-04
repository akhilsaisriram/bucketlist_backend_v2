from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id','username', 'email', 'password', 'phone', 'dob','place','ocord']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            # uid=validated_data['uid'],
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone', ''),
            dob=validated_data.get('dob', None)
        )
        return user
