from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user that enforces unique emails for authentication."""

    email = models.EmailField(unique=True)

    def __str__(self) -> str:
        return self.username or self.email


class Profile(models.Model):
    """Extends each user with public identity fields and avatar."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    time_zone = models.CharField(max_length=50, default="UTC")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.display_name


class HackerHouse(models.Model):
    """Represents a shared living space that hosts can list and manage."""
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hosted_houses",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="member_houses",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class HouseImage(models.Model):
    """Stores gallery images tied to a given hacker house."""
    house = models.ForeignKey(
        HackerHouse,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="house_images/")
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Image for {self.house.title}"


class Follow(models.Model):
    """Directed relationship used to build personalized house/event feeds."""
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self) -> str:
        return f"{self.follower} -> {self.following}"


class Event(models.Model):
    """Calendar entry for gatherings hosted by users or specific houses."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events_created",
    )
    house = models.ForeignKey(
        HackerHouse,
        on_delete=models.SET_NULL,
        related_name="events",
        null=True,
        blank=True,
    )
    location = models.CharField(max_length=255)
    is_public = models.BooleanField(default=True)
    partiful_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title
