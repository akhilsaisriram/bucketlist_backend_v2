from django.urls import path
from .views import *

urlpatterns = [
    path('create/', GroupCreateView.as_view(), name='group-create'),
    path('update/<int:pk>/', GroupUpdateView.as_view(), name='group-update'),
    path('delete/<int:pk>/', GroupDeleteView.as_view(), name='group-delete'),
    path('accept_decline/',Accept.as_view()),
    path('getgroup_accept_frends_details/',getgroup_accept_frends_details.as_view()),
]