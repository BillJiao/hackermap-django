from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Event, Follow, HackerHouse, HouseImage, Profile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Expose the custom user in the admin with email search."""

    list_display = ("username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("username",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "time_zone")
    search_fields = ("display_name", "user__username", "user__email")


@admin.register(HackerHouse)
class HackerHouseAdmin(admin.ModelAdmin):
    list_display = ("title", "host", "capacity", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "host__username", "address")


@admin.register(HouseImage)
class HouseImageAdmin(admin.ModelAdmin):
    list_display = ("house", "uploaded_at")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "start_time", "end_time", "is_public")
    list_filter = ("is_public", "start_time")
    search_fields = ("title", "location")
