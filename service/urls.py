from django.urls import path
from .views import *

urlpatterns = [
    path('putservise/', Putservice.as_view()),
    path('getdataservice/', getservice.as_view()),
    path('del/<int:service_id>/', getservice.as_view()),
]
