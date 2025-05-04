from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('update/', UpdateLocationView.as_view(), name='update'),

    path('protected/', protected_view, name='protected'),  # Add this line
]
