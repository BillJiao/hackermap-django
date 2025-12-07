from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import HackerHouse, Event

User = get_user_model()

class CreateAccountForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class HackerHouseCreateForm(forms.ModelForm):
    """Form for authenticated users to create a new house."""
    
    house_image = forms.ImageField(
        required=False,
        label="House Image",
        help_text="Upload a cover image for your house"
    )
    image_caption = forms.CharField(
        max_length=255,
        required=False,
        label="Image Caption",
        widget=forms.TextInput(attrs={'placeholder': 'Optional caption for the image'})
    )

    class Meta:
        model = HackerHouse
        fields = ['title', 'address', 'description', 'capacity']
        labels = {
            'title': 'House Name',
            'address': 'Address',
            'description': 'Description',
            'capacity': 'Member Capacity',
        }


class HackerHouseEditForm(forms.ModelForm):
    """Form for hosts to edit their house details."""
    
    new_image = forms.ImageField(
        required=False,
        label="Add New Image",
        help_text="Upload a new image to add to the gallery"
    )
    image_caption = forms.CharField(
        max_length=255,
        required=False,
        label="Image Caption",
        widget=forms.TextInput(attrs={'placeholder': 'Optional caption for the image'})
    )

    class Meta:
        model = HackerHouse
        fields = ['title', 'description', 'capacity']
        labels = {
            'title': 'House Name',
            'description': 'Description',
            'capacity': 'Member Capacity',
        }


class EventCreateForm(forms.ModelForm):
    """Form for house members to create events."""
    
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Start Time'
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='End Time'
    )
    
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_time', 'end_time', 'location', 'is_public', 'partiful_link']
        labels = {
            'title': 'Event Title',
            'description': 'Description',
            'location': 'Location',
            'is_public': 'Public Event',
            'partiful_link': 'Partiful Link (optional)',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What\'s this event about?'}),
            'location': forms.TextInput(attrs={'placeholder': 'Where is this happening?'}),
            'partiful_link': forms.URLInput(attrs={'placeholder': 'https://partiful.com/...'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError("End time must be after start time.")
        
        return cleaned_data
