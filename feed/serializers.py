from rest_framework import serializers
from .models import Feed

class FeedSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='userid.username', read_only=True)  # Fetch username from ForeignKey
    class Meta:
        model = Feed
        fields = ['userid','id','username','origin',  'ocord', 'media','mediatype','likes','dislikes', 'content' ,'created_at', 'updated_at','typeofcontent']
        read_only_fields = ['userid', 'created_at', 'updated_at']

   
