from django.urls import path
from .views import *

urlpatterns = [
    path('following/', AddFollowingView.as_view()),
    path('unfollowing/', UnFollowingView.as_view()),

    # path('follower/', AddFollowerView.as_view()),
    path('accpetfollowing/',Settings.as_view()),
    path('blockuser/',Settingsblock.as_view()),

    
    
]
