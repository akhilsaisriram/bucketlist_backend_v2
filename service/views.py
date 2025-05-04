from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Point
from .models import Service
from .serializers import serviceSerializer
from django.http import JsonResponse
from django.views import View
from azure.storage.blob import BlobServiceClient, ContentSettings
from datetime import datetime
from django.conf import settings

from django.utils.timezone import make_aware

AZURE_CONNECTION_STRING = 'BlobEndpoint=https://bucketlistv1.blob.core.windows.net/;QueueEndpoint=https://bucketlistv1.queue.core.windows.net/;FileEndpoint=https://bucketlistv1.file.core.windows.net/;TableEndpoint=https://bucketlistv1.table.core.windows.net/;SharedAccessSignature=sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2025-05-23T20:23:02Z&st=2025-01-23T12:23:02Z&spr=https&sig=5SryoZQwsdZYTnSbxmsqIK8m7mu6OvkvndkVJl7P8zw%3D'
# https://bucketlistfeed.blob.core.windows.net/feed?sp=racwdli&st=2024-11-01T12:43:26Z&se=2024-12-31T20:43:26Z&sv=2022-11-02&sr=c&sig=elUtMfr9kGwLxtqu8Py%2F03vbmZwhL9xmFjtOVO%2BFo2U%3D
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


class Putservice(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
            data = dict(request.data)
            print(data)

            # Helper function to safely extract single-item lists
            def unwrap_field(field_name):
                return data[field_name][0] if isinstance(data.get(field_name), list) else data.get(field_name)

            # Convert fields to required format if they exist
            data['origin'] = unwrap_field('origin')
            data['discription'] = unwrap_field('discription')
            data['servicetype'] = unwrap_field('servicetype')
            data['service_name'] = unwrap_field('service_name')
            data['contact_number1'] = unwrap_field('contact_number1')

            data['contact_number2'] = unwrap_field('contact_number2')

            
            # Parse available_days field to list if it's in JSON string format
            try:
                print(data['available_days'])
                data['available_days'] = data['available_days']
            except (json.JSONDecodeError, KeyError, TypeError):
                return Response({"error": "Invalid format for available_days"}, status=status.HTTP_400_BAD_REQUEST)

            # Parse and format start_time and end_time to TimeField compatible values
            try:
                print(data['start_time'])
                data['start_time'] = data['start_time'][0]
                data['end_time'] =data['end_time'][0]
            except (ValueError, TypeError, KeyError):
                return Response({"error": "Invalid format for start_time or end_time"}, status=status.HTTP_400_BAD_REQUEST)

            # Handle file uploads for media and proofid fields
            def handle_file_upload(field_name):
                file = request.FILES.get(field_name)
                if file:
                    blob_name = file.name
                    media_type = 'image' if file.content_type.startswith('image/') else 'video' if file.content_type.startswith('video/') else None
                    if not media_type:
                        return Response({"error": "Unsupported media type"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    media_url = upload_media_to_azure(file, blob_name)
                    if not media_url:
                        return Response({"error": "Failed to upload media"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    return media_url, media_type
                return None, None

            media_url, media_type = handle_file_upload('media')
            if media_url:
                data['media'] = [media_url]
                data['mediatype'] = [media_type]

            proofid_url, _ = handle_file_upload('proofid')
            if proofid_url:
                data['proofid'] = [proofid_url]

            # Parse coordinates if available
            try:
                coordinates_str = unwrap_field('ocord[coordinates]')
                coordinates = json.loads(coordinates_str) if coordinates_str else []
                if len(coordinates) == 2:
                    data['ocord'] = {"type": "Point", "coordinates": coordinates}
                else:
                    return Response({"error": "Invalid coordinates format"}, status=status.HTTP_400_BAD_REQUEST)
            except (json.JSONDecodeError, ValueError, KeyError):
                return Response({"error": "Error parsing coordinates"}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize and save
            serializer = serviceSerializer(data=data)
            if serializer.is_valid():
                coordinates = data.get('ocord', {}).get('coordinates', [])
                if len(coordinates) == 2:
                    serializer.validated_data['ocord'] = Point(coordinates[1], coordinates[0], srid=4326)
                serializer.save(userid=request.user)
                return Response({"message": "Service created successfully!", "service": serializer.data}, status=status.HTTP_201_CREATED)

            print(serializer.errors)  # Debugging line to inspect validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


   
class getservice(APIView):
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        # Get all Feed objects for the authenticated user
        feeds = Service.objects.filter(userid=request.user)

        # Serialize the Feed objects
        serializer = serviceSerializer(feeds, many=True)

        # Return the serialized feed data
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def delete(self, request, service_id):
        try:
            # Check if the service exists and belongs to the authenticated user
            service = Service.objects.get(id=service_id)
            service.delete()
            print("deleted")
            return Response({"message": "Service deleted successfully."}, status=status.HTTP_200_OK)
        except Service.DoesNotExist:
            return Response(
                {"error": "Service not found or you do not have permission to delete it."},
                status=status.HTTP_404_NOT_FOUND
            )
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q  # Import Q for complex queries

class Nearbyservise(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lat = request.query_params.get('lat')  # Get latitude from query parameters
        lon = request.query_params.get('lon')  # Get longitude from query parameters
        radius = request.query_params.get('radius', 10000)  # Default radius to 10 km

        if lat is None or lon is None:
            return Response({"error": "Latitude and longitude are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Convert the latitude and longitude to a Point object
            user_location = Point( float(lat),float(lon), srid=4326)
            print(f"User Location: {user_location}")  # Debugging

            # Filter Bucketlist items within the given radius and annotate with distances to both ocord and dcord
            nearby_locations = Service.objects.annotate(
                distance_to_ocord=Distance('ocord', user_location),
            ).filter(
                Q(distance_to_ocord__lte=radius) | Q(distance_to_dcord__lte=radius)
            ).order_by('distance_to_ocord')

            print(f"Nearby service Locations Count: {nearby_locations.count()}")  # Debugging

            # Serialize the nearby locations
            serializer = serviceSerializer(nearby_locations, many=True)
            result = []
            for item, location in zip(serializer.data, nearby_locations):
                item['distance_to_ocord'] = location.distance_to_ocord.m  # Distance to ocord in meters
                result.append(item)

            return Response(result, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Invalid coordinates."}, status=status.HTTP_400_BAD_REQUEST)

