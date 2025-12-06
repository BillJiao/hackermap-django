from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    HackerHouseListView, 
    HackerHouseDetailView, 
    UserProfileDetailView,
    JoinHouseView,
    LeaveHouseView,
    ToggleFollowView,
    ToggleFollowHouseView,
    CreateAccountView,
    EventCalendarView,
)

urlpatterns = [
    path('houses/', HackerHouseListView.as_view(), name='hackerhouse_list'),
    path('houses/<int:pk>/', HackerHouseDetailView.as_view(), name='hackerhouse_detail'),
    path('houses/<int:pk>/join/', JoinHouseView.as_view(), name='join_house'),
    path('houses/<int:pk>/leave/', LeaveHouseView.as_view(), name='leave_house'),
    path('houses/<int:pk>/follow/', ToggleFollowHouseView.as_view(), name='toggle_follow_house'),
    path('users/<int:pk>/', UserProfileDetailView.as_view(), name='user_profile_detail'),
    path('users/<int:pk>/follow/', ToggleFollowView.as_view(), name='toggle_follow'),
    path('events/', EventCalendarView.as_view(), name='event_calendar'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('create_account/', CreateAccountView.as_view(), name='create_account'),
]
