from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from bucketlist.models import Bucketlist
from bucketlist.serializers import BucketlistSerializer
from feed.models import Feed
from feed.serializers import FeedSerializer
from service.models import Service
from service.serializers import serviceSerializer

from .utils import get_objects_within_radius
from members.models import CustomUser
from members.serializers import  UserSerializer
class Findserch(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract latitude, longitude, and radius from the request
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        radius_km = request.data.get('radius', 10)  # Default radius is 10 km

        if lat is None or lng is None:
            return Response(
                {"error": "Latitude and longitude are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            lat, lng = float(lat), float(lng)
        except ValueError:
            return Response(
                {"error": "Invalid latitude or longitude format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Fetch and serialize data
            bucketlist_data = get_objects_within_radius(Bucketlist, BucketlistSerializer, lat, lng, radius_km, ['ocord', 'dcord'])
            feed_data = get_objects_within_radius(Feed, FeedSerializer, lat, lng, radius_km, ['ocord'])
            service_data = get_objects_within_radius(Service, serviceSerializer, lat, lng, radius_km, ['ocord'])
            people_data = get_objects_within_radius(CustomUser, UserSerializer, lat, lng, radius_km, ['ocord'])

            # Prepare structured response
            response_data = {
                "bucketlists": bucketlist_data,
                "feeds": feed_data,
                "services": service_data,
                "people":people_data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
