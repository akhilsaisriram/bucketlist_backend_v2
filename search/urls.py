from django.urls import path
from .views import *

urlpatterns = [
    path('find/', Findserch.as_view()),
]