from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import HackerHouse, User

# Create your views here.
# HackerHouseListView is a class-based view that lists all hacker houses
class HackerHouseListView(ListView):
    model = HackerHouse
    template_name = "hackerhouse_list.html"
    context_object_name = "hackerhouses" 

    def get_queryset(self):
        return HackerHouse.objects.prefetch_related('images').all()    
        
# HackerHouseDetailView is a class-based view that displays a single hacker house
class HackerHouseDetailView(DetailView):
    model = HackerHouse
    template_name = "hackerhouse_detail.html"
    context_object_name = "hackerhouse"

    def get_queryset(self):
        return HackerHouse.objects.select_related('host').prefetch_related('images', 'members').all()

# UserProfileDetailView is a class-based view that displays a single user profile
class UserProfileDetailView(DetailView):
    model = User
    template_name = "user_profile_detail.html"
    context_object_name = "user"

    def get_queryset(self):
        return User.objects.select_related('profile').all()