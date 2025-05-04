from django.urls import path
from .views import *

urlpatterns = [
    path('putfeed/', Putfeed.as_view()),
    path('getfeed/', Putfeed.as_view()),
    path('allfeed/',Getallfeed.as_view()),
    path('comments/<int:feed_id>/',GetFeedComments.as_view()),
    path('feedaction/<int:feed_id>/', FeedActionView.as_view(), name='feed-action'),
    
]
