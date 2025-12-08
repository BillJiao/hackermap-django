# File: apps.py
# Author: Bill Jiao (jiaobill@bu.edu), 12/8/2024
# Description: Django app configuration for the HackerMap project application.

from django.apps import AppConfig


class ProjectConfig(AppConfig):
    """Configuration class for the project Django application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project'
