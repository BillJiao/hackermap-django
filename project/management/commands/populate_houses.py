# File: populate_houses.py
# Author: Bill Jiao (jiaobill@bu.edu), 12/8/2024
# Description: Django management command to populate the database with sample
#              hacker houses for testing and demonstration purposes.

import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from project.models import HackerHouse

User = get_user_model()


class Command(BaseCommand):
    """Management command to create sample hacker houses in the database."""
    help = 'Populates the database with sample hacker houses'

    def handle(self, *args, **kwargs):
        # Create or get a sample host user
        user, created = User.objects.get_or_create(
            username='sample_host',
            defaults={'email': 'host@example.com'}
        )
        if created:
            user.set_password('password')
            user.save()

        # Word lists for generating random house names
        adjectives = ['Cyber', 'Quantum', 'Neural', 'Binary', 'Silicon', 'Digital', 'Crypto', 'Tech', 'Code', 'Data']
        nouns = ['Haven', 'Bunker', 'Fortress', 'Lab', 'Hub', 'Nexus', 'Base', 'Station', 'Loft', 'Manor']
        cities = ['San Francisco', 'New York', 'Austin', 'Miami', 'Seattle', 'Berlin', 'London', 'Tokyo', 'Toronto', 'Singapore']

        # Generate 20 sample houses with random attributes
        houses = []
        for _ in range(20):
            title = f"{random.choice(adjectives)} {random.choice(nouns)}"
            address = f"{random.randint(100, 9999)} {random.choice(['Market', 'Mission', 'Broadway', 'Main', 'First'])} St, {random.choice(cities)}"
            description = "A cutting-edge co-living space for builders, hackers, and dreamers. Join a community of like-minded individuals working on the next big thing. High-speed internet, ergonomic workstations, and weekly demo nights included."
            
            house = HackerHouse(
                host=user,
                title=title,
                description=description,
                address=address,
                capacity=random.randint(4, 20),
                is_active=True
            )
            houses.append(house)

        # Bulk insert all houses at once for efficiency
        HackerHouse.objects.bulk_create(houses)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(houses)} hacker houses'))
