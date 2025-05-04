from django.urls import path
from .views import *

urlpatterns = [
    path('putdata/', PutBucketlist.as_view(), name='bucketlist'),
    path('nearby/', NearbyBucketlist.as_view(), name='nearby-bucketlist'),
    path('nearbypagination/', NearbyBucketlistpagination.as_view(), name='nearby-bucketlist'),

    
]
