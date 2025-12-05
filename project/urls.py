from django.urls import path
from .views import HackerHouseListView, HackerHouseDetailView, UserProfileDetailView

urlpatterns = [
    path('houses/', HackerHouseListView.as_view(), name='hackerhouse_list'),
    path('houses/<int:pk>/', HackerHouseDetailView.as_view(), name='hackerhouse_detail'),
    path('users/<int:pk>/', UserProfileDetailView.as_view(), name='user_profile_detail'),
]
