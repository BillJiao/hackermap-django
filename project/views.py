from django.shortcuts import render
from django.views.generic import ListView
from .models import HackerHouse

# Create your views here.
class HackerHouseListView(ListView):
    model = HackerHouse
    template_name = "hackerhouse_list.html"
    context_object_name = "hackerhouses" 

    def get_queryset(self):
        return HackerHouse.objects.prefetch_related('images').all()    
        
    