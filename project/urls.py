from django.urls import path
from .views import HackerHouseListView

urlpatterns = [
    path('houses/', HackerHouseListView.as_view(), name='hackerhouse_list'),
]
