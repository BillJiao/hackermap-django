from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, View, CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from .models import HackerHouse, HouseImage, User, Follow, Event
from .forms import CreateAccountForm, HackerHouseEditForm, HackerHouseCreateForm, EventCreateForm

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        house = self.object
        
        # Count followers for this house
        context['followers_count'] = Follow.objects.filter(following_house=house).count()
        
        if user.is_authenticated:
            context['is_member'] = house.members.filter(pk=user.pk).exists()
            context['is_host'] = house.host == user
            context['is_following'] = Follow.objects.filter(
                follower=user,
                following_house=house
            ).exists()
        else:
            context['is_following'] = False
        return context

# JoinHouseView handles authenticated users joining a house
class JoinHouseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        house = get_object_or_404(HackerHouse, pk=pk)
        user = request.user
        
        # Check if already a member
        if house.members.filter(pk=user.pk).exists():
            messages.info(request, "You are already a member of this house.")
        # Check if house is at capacity
        elif house.members.count() >= house.capacity:
            messages.warning(request, "This house is at full capacity.")
        # Check if house is active
        elif not house.is_active:
            messages.warning(request, "This house is not accepting new members.")
        else:
            house.members.add(user)
            messages.success(request, f"You have joined {house.title}!")
        
        return redirect('hackerhouse_detail', pk=pk)

# LeaveHouseView handles authenticated users leaving a house
class LeaveHouseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        house = get_object_or_404(HackerHouse, pk=pk)
        user = request.user
        
        # Can't leave if you're the host
        if house.host == user:
            messages.warning(request, "As the host, you cannot leave your own house.")
        elif house.members.filter(pk=user.pk).exists():
            house.members.remove(user)
            messages.success(request, f"You have left {house.title}.")
        else:
            messages.info(request, "You are not a member of this house.")
        
        return redirect('hackerhouse_detail', pk=pk)

# UserProfileDetailView is a class-based view that displays a single user profile
class UserProfileDetailView(DetailView):
    model = User
    template_name = "user_profile_detail.html"
    context_object_name = "profile_user"

    def get_queryset(self):
        return User.objects.select_related('profile').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.object
        current_user = self.request.user
        
        # Count followers (users following this profile) and following (users + houses this profile follows)
        context['followers_count'] = Follow.objects.filter(following_user=profile_user).count()
        context['following_count'] = Follow.objects.filter(follower=profile_user).count()
        
        # Check if current user is following this profile
        if current_user.is_authenticated:
            context['is_following'] = Follow.objects.filter(
                follower=current_user,
                following_user=profile_user
            ).exists()
            context['is_own_profile'] = current_user == profile_user
        else:
            context['is_following'] = False
            context['is_own_profile'] = False
        
        # Get the house this profile was accessed from (if any)
        from_house_id = self.request.GET.get('from_house')
        if from_house_id:
            try:
                context['from_house'] = HackerHouse.objects.get(pk=from_house_id)
            except HackerHouse.DoesNotExist:
                context['from_house'] = None
        else:
            context['from_house'] = None
        
        return context


# ToggleFollowView handles authenticated users following/unfollowing other users
class ToggleFollowView(LoginRequiredMixin, View):
    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        current_user = request.user
        from_house = request.POST.get('from_house')
        
        # Build redirect URL with from_house parameter if present
        redirect_url = reverse('user_profile_detail', kwargs={'pk': pk})
        if from_house:
            redirect_url += f"?from_house={from_house}"
        
        # Can't follow yourself
        if target_user == current_user:
            messages.warning(request, "You cannot follow yourself.")
            return redirect(redirect_url)
        
        # Check if already following
        follow_relation = Follow.objects.filter(
            follower=current_user,
            following_user=target_user
        ).first()
        
        if follow_relation:
            # Unfollow
            follow_relation.delete()
            messages.success(request, f"You have unfollowed {target_user.profile.display_name or target_user.username}.")
        else:
            # Follow
            Follow.objects.create(follower=current_user, following_user=target_user)
            messages.success(request, f"You are now following {target_user.profile.display_name or target_user.username}!")
        
        return redirect(redirect_url)


# ToggleFollowHouseView handles authenticated users following/unfollowing houses
class ToggleFollowHouseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        house = get_object_or_404(HackerHouse, pk=pk)
        current_user = request.user
        
        # Check if already following
        follow_relation = Follow.objects.filter(
            follower=current_user,
            following_house=house
        ).first()
        
        if follow_relation:
            # Unfollow
            follow_relation.delete()
            messages.success(request, f"You have unfollowed {house.title}.")
        else:
            # Follow
            Follow.objects.create(follower=current_user, following_house=house)
            messages.success(request, f"You are now following {house.title}!")
        
        return redirect('hackerhouse_detail', pk=pk)

# CreateAccountView handles user account creation
class CreateAccountView(CreateView):
    model = User
    form_class = CreateAccountForm
    template_name = 'registration/create_account_form.html'
    success_url = reverse_lazy('login')

# EventCalendarView is a class-based view that lists events from followed houses
class EventCalendarView(TemplateView):
    template_name = 'event_calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_authenticated:
            # Get houses the user follows
            followed_house_ids = Follow.objects.filter(
                follower=user,
                following_house__isnull=False
            ).values_list('following_house_id', flat=True)
            
            # Filter events to only those from followed houses
            context['events'] = Event.objects.filter(
                house_id__in=followed_house_ids
            ).select_related('created_by', 'house')
        else:
            # No events for unauthenticated users
            context['events'] = Event.objects.none()
        
        return context


# EditHouseView allows hosts to edit their house details
class EditHouseView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = HackerHouse
    form_class = HackerHouseEditForm
    template_name = 'house_edit.html'
    context_object_name = 'hackerhouse'

    def test_func(self):
        """Only allow the host of the house to edit it."""
        house = self.get_object()
        return self.request.user == house.host

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to edit this house.")
        return redirect('hackerhouse_detail', pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['existing_images'] = self.object.images.all()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle new image upload
        new_image = form.cleaned_data.get('new_image')
        if new_image:
            caption = form.cleaned_data.get('image_caption', '')
            HouseImage.objects.create(
                house=self.object,
                image=new_image,
                caption=caption
            )
            messages.success(self.request, "Image added successfully!")
        
        messages.success(self.request, f"'{self.object.title}' has been updated!")
        return response

    def get_success_url(self):
        return reverse('hackerhouse_detail', kwargs={'pk': self.object.pk})


# DeleteHouseImageView allows hosts to remove images from their house
class DeleteHouseImageView(LoginRequiredMixin, View):
    def post(self, request, pk, image_pk):
        house = get_object_or_404(HackerHouse, pk=pk)
        
        # Only the host can delete images
        if request.user != house.host:
            messages.error(request, "You don't have permission to delete this image.")
            return redirect('edit_house', pk=pk)
        
        image = get_object_or_404(HouseImage, pk=image_pk, house=house)
        image.delete()
        messages.success(request, "Image deleted successfully!")
        
        return redirect('edit_house', pk=pk)


# CreateHouseView allows authenticated users to create a new house
class CreateHouseView(LoginRequiredMixin, CreateView):
    model = HackerHouse
    form_class = HackerHouseCreateForm
    template_name = 'house_create.html'

    def form_valid(self, form):
        # Set the current user as the host
        form.instance.host = self.request.user
        response = super().form_valid(form)
        
        # Handle image upload
        house_image = form.cleaned_data.get('house_image')
        if house_image:
            caption = form.cleaned_data.get('image_caption', '')
            HouseImage.objects.create(
                house=self.object,
                image=house_image,
                caption=caption
            )
        
        # Add the host as a member of the house
        self.object.members.add(self.request.user)
        
        messages.success(self.request, f"'{self.object.title}' has been created!")
        return response

    def get_success_url(self):
        return reverse('hackerhouse_detail', kwargs={'pk': self.object.pk})


# CreateHouseEventView allows house members to create events for a house
class CreateHouseEventView(LoginRequiredMixin, View):
    def get(self, request, pk):
        house = get_object_or_404(HackerHouse, pk=pk)
        user = request.user
        
        # Check if user is a member of this house
        is_member = house.members.filter(pk=user.pk).exists()
        is_host = house.host == user
        
        if not (is_member or is_host):
            messages.error(request, "Only house members can create events.")
            return redirect('hackerhouse_detail', pk=pk)
        
        return render(request, 'event_create.html', {'hackerhouse': house})
    
    def post(self, request, pk):
        house = get_object_or_404(HackerHouse, pk=pk)
        user = request.user
        
        # Check if user is a member of this house
        is_member = house.members.filter(pk=user.pk).exists()
        is_host = house.host == user
        
        if not (is_member or is_host):
            messages.error(request, "Only house members can create events.")
            return redirect('hackerhouse_detail', pk=pk)
        
        form = EventCreateForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = user
            event.house = house
            event.save()
            messages.success(request, f"Event '{event.title}' has been created!")
            return redirect('hackerhouse_detail', pk=pk)
        else:
            # Re-render form with errors
            return render(request, 'event_create.html', {
                'hackerhouse': house,
                'form': form,
            })
