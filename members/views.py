from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')  # Get the email instead of username
        password = request.data.get('password')
        
        try:
            # Get the user by email
            user = CustomUser.objects.get(email=email)
            # Authenticate the user
            user = authenticate(username=user.username, password=password)  # Use the username for authentication
            
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

from bucketlist.models import Bucketlist
from frends.models import Frends
from bucketlist.serializers import BucketlistSerializer
from  frends.serializers import FrendSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    # user = request.user
    name = request.query_params.get('name', None)
    
    # Get user based on the `name` if provided, else fallback to `request.user`
    if name:
        user = get_object_or_404(User, username=name)
    else:
        user = request.user
    Bucket = Bucketlist.objects.filter(uid_id=user.id)
    Frend = Frends.objects.filter(userid_id=user.id)
    bucketlist_serialized = BucketlistSerializer(Bucket, many=True).data
    frends_serialized = FrendSerializer(Frend, many=True).data
    return Response({
        'idd':user.id,
        'place':user.place,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'dob': str(user.dob) if user.dob else 'N/A',  # Add a comma here
        'bucketlist': bucketlist_serialized,
        'frends': frends_serialized
    })


from django.contrib.gis.geos import Point


class UpdateLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            place = request.data.get("place")
            lat = request.data.get("lat")
            lng = request.data.get("lng")

            if not place or lat is None or lng is None:
                return Response(
                    {"error": "Place, latitude, and longitude are required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            coo= Point(lat, lng, srid=4326)
            print(coo) 
            user.place = place
            user.ocord = coo
            user.save()

            return Response(
                {"message": "Location updated successfully."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
