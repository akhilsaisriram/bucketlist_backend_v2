from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Point  # Import Point
from .models import Bucketlist
from .serializers import BucketlistSerializer
from django.contrib.gis.geos import Point,GEOSGeometry,MultiPoint,LineString
from django.contrib.gis.db.models.functions import Distance
from urllib.parse import unquote
import polyline
from feed.models import Feed
from feed.serializers import FeedSerializer
import logging

logger = logging.getLogger(__name__)
class PutBucketlist(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract bucket data from request.data
        bucket_data = request.data.get("bucket", {})

        # Check for latitude and longitude fields for origin and destination
        try:
            # Convert 'ocord' and 'dcord' fields to Point objects using olat/olon and dlat/dlon
            ocord = Point(bucket_data['olat'], bucket_data['olon'])
            dcord = Point(bucket_data['dlat'], bucket_data['dlon'])

            # Prepare data for serialization
            data = {
                "uid": request.user.id,  # User ID
                "origin": bucket_data.get("origin"),
                "destination": bucket_data.get("destination"),
                "bucket": bucket_data.get("name"),
                "ocord": ocord,
                "dcord": dcord,
                "start_date": bucket_data.get("startDate"),
                "end_date": bucket_data.get("endDate"),
            }

            # Deserialize and validate the data
            serializer = BucketlistSerializer(data=data)
            if serializer.is_valid():
                # Save and associate the record with the authenticated user
                serializer.save(uid=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            # If validation fails, return errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except KeyError as e:
            # Handle missing required fields with an appropriate response
            return Response({"error": f"Missing field: {e.args[0]}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Handle any other unexpected errors
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



from django.db.models import Q  # Import Q for complex queries

from .utils import polylinedata
class NearbyBucketlist(APIView):
    permission_classes = [IsAuthenticated]

    
    def post(self, request):
        """
        Handle POST request for retrieving nearby bucket lists and feeds 
        based on origin, destination, and polyline data.
        """
        try:
            # Extract input data
            ocord = request.data.get("ocord")  # Origin WKT
            dcord = request.data.get("dcord")  # Destination WKT
            polyline_text = request.data.get("polyline")  # Encoded polyline
            radius = float(request.data.get("radius", 10000))  # Default radius: 10 km

            # Validate required fields
            if not ocord or not dcord:
                return Response(
                    {"error": "Both origin and destination coordinates are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Decode WKT and create GEOSGeometry objects with SRID 4326
            origin_point = GEOSGeometry(unquote(ocord))
            destination_point = GEOSGeometry(unquote(dcord))

            # Set SRID for the origin and destination points if not already set
            origin_point.srid = 4326
            destination_point.srid = 4326

            # Query nearby bucketlist locations
            nearby_locations = Bucketlist.objects.annotate(
                distance_to_ocord=Distance("ocord", origin_point),
                distance_to_dcord=Distance("dcord", destination_point),
            ).filter(
                (Q(distance_to_ocord__lte=radius) | Q(distance_to_dcord__lte=radius)) & ~Q(uid=request.user.id)
            ).order_by("distance_to_ocord")

            # Serialize bucketlist results
            bucketlist_serializer = BucketlistSerializer(nearby_locations, many=True)
            bucket_results = [
                {**item,
                 "distance_to_ocord": location.distance_to_ocord.m,
                 "distance_to_dcord": location.distance_to_dcord.m}
                for item, location in zip(bucketlist_serializer.data, nearby_locations)
            ]

            # Query feeds based on polyline
            feed_results = []
            if polyline_text:
                # Decode polyline into coordinates
              
                aa=polylinedata(polyline_text)

            # Combine results
            response_data = {
                "bucket": bucket_results,
                "feed": aa,
            }
            print("data",bucket_results)
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log error details for debugging
            logger.error(f"Error in NearbyBucketlist API: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Invalid data: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        


from rest_framework.pagination import PageNumberPagination

class NearbyBucketlistpagination(APIView):
    permission_classes = [IsAuthenticated]

    
    def post(self, request):
        """
        Handle POST request for retrieving nearby bucket lists and feeds 
        based on origin, destination, and polyline data.
        """
        try:
            # Extract input data
            ocord = request.data.get("ocord")  # Origin WKT
            dcord = request.data.get("dcord")  # Destination WKT
            polyline_text = request.data.get("polyline")  # Encoded polyline
            radius = float(request.data.get("radius", 10000))  # Default radius: 10 km

           
            # Validate required fields
            if not ocord or not dcord:
                return Response(
                    {"error": "Both origin and destination coordinates are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Decode WKT and create GEOSGeometry objects with SRID 4326
            origin_point = GEOSGeometry(unquote(ocord))
            destination_point = GEOSGeometry(unquote(dcord))

            # Set SRID for the origin and destination points if not already set
            origin_point.srid = 4326
            destination_point.srid = 4326

            # Query nearby bucketlist locations
            nearby_locations = Bucketlist.objects.annotate(
                distance_to_ocord=Distance("ocord", origin_point),
                distance_to_dcord=Distance("dcord", destination_point),
            ).filter(
                (Q(distance_to_ocord__lte=radius) | Q(distance_to_dcord__lte=radius)) & ~Q(uid=request.user.id)
            ).order_by("distance_to_ocord")

            # Serialize bucketlist results
            paginator = PageNumberPagination()
            paginator.page_size = 10  # Adjust page size as needed
            paginated_results = paginator.paginate_queryset(nearby_locations, request)

            # Serialize results
            bucketlist_serializer = BucketlistSerializer(paginated_results, many=True)
            bucket_results = [
                {**item, "distance_to_ocord": location.distance_to_ocord.m, "distance_to_dcord": location.distance_to_dcord.m}
                for item, location in zip(bucketlist_serializer.data, paginated_results)
            ]

            # Query feeds based on polyline
            feed_results = []
            if polyline_text:
                # Decode polyline into coordinates
              
                aa=polylinedata(polyline_text)

            # Combine results
            response_data = {
                "bucket": bucket_results,
                "feed": aa,
            }
            print("data",bucket_results)
            # return Response(response_data, status=status.HTTP_200_OK)
            return paginator.get_paginated_response({"bucket": bucket_results, "feed": aa})


        except Exception as e:
            # Log error details for debugging
            logger.error(f"Error in NearbyBucketlist API: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Invalid data: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        




class Nearbyplaces(APIView):
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
            nearby_locations = Feed.objects.annotate(
                distance_to_ocord=Distance('ocord', user_location),
            ).filter(
                Q(distance_to_ocord__lte=radius) | Q(distance_to_dcord__lte=radius)
            ).order_by('distance_to_ocord')

            print(f"Nearby places Locations Count: {nearby_locations.count()}")  # Debugging

            # Serialize the nearby locations
            serializer = FeedSerializer(nearby_locations, many=True)
            result = []
            for item, location in zip(serializer.data, nearby_locations):
                item['distance_to_ocord'] = location.distance_to_ocord.m  # Distance to ocord in meters
                result.append(item)

            return Response(result, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Invalid coordinates."}, status=status.HTTP_400_BAD_REQUEST)
