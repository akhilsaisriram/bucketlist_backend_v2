from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Point
from .models import Feed
from .serializers import FeedSerializer
from django.http import JsonResponse
from django.views import View
from azure.storage.blob import BlobServiceClient, ContentSettings

from django.conf import settings

AZURE_CONNECTION_STRING = ''
AZURE_CONTAINER_NAME = 'bucket'

def upload_media_to_azure(file, blob_name):
    """
    Upload an image or video to Azure Blob Storage.
    
    :param file: File object (e.g., from request.FILES['file'])
    :param blob_name: The name for the blob in Azure storage
    :return: URL of the uploaded file
    """
    try:
        # Create the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        
        # Get a client to interact with the container
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        
        # Upload the file to Azure Blob Storage
        blob_client = container_client.get_blob_client(blob_name)
        
        # Set content type based on the file
        content_settings = ContentSettings(content_type=file.content_type)
        
        # Upload the file and track the progress
        with file.open("rb") as data:
            blob_client.upload_blob(data, content_settings=content_settings, overwrite=True,connection_timeout=500)
        print(blob_client.url)
        return blob_client.url  # URL for accessing the uploaded media
    
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None 
import json  # Add this import to handle string to list conversion
from django.contrib.gis.geos import Point

class Putfeed(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = dict(request.data)
        print(f"Received data: {data}")  # Log the data for debugging

        # Convert 'origin' and 'content' fields from lists to strings if needed
        data['origin'] = data.get('origin', [""])[0]
        data['content'] = data.get('content', [""])[0]
        try:
            # Convert latitude and longitude to floats
            latitude = float(data.get('olat', [""])[0])
            longitude = float(data.get('olon', [""])[0])
            ocord = Point(latitude, longitude, srid=4326)
            data['ocord'] = ocord
        except (ValueError, TypeError):
            return Response({"error": "Invalid latitude or longitude values"}, status=status.HTTP_400_BAD_REQUEST)

        # Handle the file upload (image or video)
        if 'file' in request.FILES:
            file = request.FILES['file']
            blob_name = file.name

            # Upload the file to Azure Blob Storage
            file_url = upload_media_to_azure(file, blob_name)

            if file_url:
                data['media'] = file_url
                data['mediatype'] = 'video' if 'video' in file.content_type else 'image'
            else:
                return Response({"error": "Failed to upload file"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Parse and handle coordinates if provided
      

        # Serialize and save data
        serializer = FeedSerializer(data=data)
        if serializer.is_valid():
            serializer.save(userid=request.user)
            return Response({"message": "Feed created successfully!", "feed": serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
    def get(self, request):
        # Get all Feed objects for the authenticated user
        feeds = Feed.objects.filter(userid=request.user)

        # Serialize the Feed objects
        serializer = FeedSerializer(feeds, many=True)

        # Return the serialized feed data
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# from groups.rabbitmq import publish
# class testrabit(APIView):
#     def get(self, request):
#         publish()
#         return Response({'message': 'Message published'})


from frends.models import Frends
from admin.neo4j_utils import Neo4jClient
import time
import random
from django.db.models import Count, Func, F
from django.contrib.postgres.fields import ArrayField
from django.core.cache import cache

from frends.serializers import FrendSerializer
class Getallfeed(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cache_key = f'feeds_{request.user.id}'
        cached_feeds = cache.get(cache_key)
        if cached_feeds:
            # If the data is cached, return the cached response
            print("Returning cached feeds")
            return Response({"data": cached_feeds}, status=status.HTTP_200_OK)

        neo4j_client = Neo4jClient()
        max_retries = 3  # Maximum number of retry attempts
        retry_delay = 2  # Delay in seconds before retrying
        node=[]
        try:
            # Attempt to create a relationship (example with user ID 1)
            node=neo4j_client.print_connected_nodes(request.user.id, request.data.get('level'))
            # print(node)
            # If successful, return a success response
            # return Response({"message": "connected nodes are {nodes} "}, status=status.HTTP_200_OK)
            
        except Exception as e:
             print(f"Attempt {e}: Error connecting to Neo4j - {e}")
        
        # Close the client after attempts
        print(node)
       
        neo4j_client.close()
        user_ids = [user['id'] for user in node]
        # print(user_ids)

#celabratys
        frends = Frends.objects.all()
        # Create a list of tuples (frend, follower_count)
        influ = [(frend, len(frend.followers)) for frend in frends]

        # Sort by follower count descending
        influ.sort(key=lambda x: x[1], reverse=True)

        # Get the top 10 percent
        top_10_percent_count = max(1, len(influ) // 10)
        top_influencers = influ[:top_10_percent_count]
        top_influencer_ids = [f[0].userid.id for f in top_influencers]
        # print(top_influencer_ids)

        totalids=top_influencer_ids + user_ids
        feeds = Feed.objects.filter(userid_id__in=totalids)
        fe=Feed.objects.all()
        serializera = FeedSerializer(fe, many=True)     

        ids = [feed.id for feed in feeds]       
        # print(ids)
        total_feed_count = Feed.objects.count()
        top_10_percent_count = max(1, int(total_feed_count * 0.10))  # Ensure at least one feed

        # Fetch the IDs of the top 10% most liked feeds
        top_10_percent_feeds = Feed.objects.exclude(id__in=ids).order_by('-likes')[:top_10_percent_count]
        # print(top_10_percent_feeds)

        # Combine both sets of feeds
        all_feeds = feeds |top_10_percent_feeds
        # print(all_feeds)
        all_feeds_list = list(all_feeds)  # Convert QuerySet to a list
        random.shuffle(all_feeds_list)  # Shuffle the list

        # Serialize the shuffled feeds
        serializer = FeedSerializer(all_feeds_list, many=True)     
        
        
        cache.set(cache_key, serializer.data, timeout=60*60)  # Cache for 60 seconds
        
        # If all attempts fail, return an error response
        return Response({"data": serializera.data}, 
                        status=status.HTTP_200_OK)

       
        

from django.shortcuts import get_object_or_404

from rest_framework.exceptions import ValidationError
class FeedActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, feed_id):
        # Get the feed object
        feed = get_object_or_404(Feed, id=feed_id)
      
        action_type = request.data.get("actionType")
        data = request.data.get("data")
        print(action_type,data)
        if not action_type:
            raise ValidationError("Action type is required.")
        
        user = request.user

        if action_type == "like":
            # Check if the user has already liked the feed
            if user.id in feed.liked_by:
                print("You have already liked this feed")
                return JsonResponse({"status": "error", "message": "You have already liked this feed."}, status=200)

            if user.id in feed.disliked_by:
                # Remove user from disliked list if they previously disliked
                feed.disliked_by.remove(user.id)
                feed.disliked_by -=1

            # Add user to liked list and update likes count
            feed.liked_by.append(user.id)
            feed.likes += 1
            feed.save()
            print("likes")
            return JsonResponse({"status": "success", "likes": feed.likes}, status=201)

        elif action_type == "dislike":
            # Check if the user has already disliked the feed
            if user.id in feed.disliked_by:
                print("You have already disliked this feed")
                return JsonResponse({"status": "error", "message": "You have already disliked this feed."}, status=200)

            if user.id in feed.liked_by:
                # Remove user from liked list if they previously liked
                print("user.id ")
                feed.liked_by.remove(user.id)
                feed.liked_by -=1

            # Add user to disliked list and update dislikes count
            feed.disliked_by.append(user.id)
            feed.dislikes += 1
            feed.save()
            print("dis")
            return JsonResponse({"status": "success", "dislikes": feed.dislikes}, status=201)

        elif action_type == "comment":
            # Handle the comment action as you previously defined
            comment_text = data.get("comment", "").strip()
            if not comment_text:
                raise ValidationError("Comment cannot be empty.")
            
            new_comment = {
                "user_id": user.id,
                "username": user.username,
                "comment": comment_text
            }

            feed.comments.append(new_comment)
            feed.save()

            return JsonResponse({"status": "success", "message": "Comment added successfully."}, status=201)

        else:
            raise ValidationError("Invalid action type. Use 'like', 'dislike', or 'comment'.")

class GetFeedComments(APIView):
    def get(self, request, feed_id):
        # Retrieve the feed instance or return a 404 error
        feed = get_object_or_404(Feed, id=feed_id)
        
        # Extract comments from the feed
        comments = feed.comments  # JSONField holds the comments as a list
        
        # Return the comments in the response
        return Response({         
            "data": comments
        }, status=status.HTTP_200_OK)
