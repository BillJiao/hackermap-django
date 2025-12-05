from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import HackerHouse, User, Follow

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
        if user.is_authenticated:
            context['is_member'] = self.object.members.filter(pk=user.pk).exists()
            context['is_host'] = self.object.host == user
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
        
        # Count followers and following
        context['followers_count'] = Follow.objects.filter(following=profile_user).count()
        context['following_count'] = Follow.objects.filter(follower=profile_user).count()
        
        # Check if current user is following this profile
        if current_user.is_authenticated:
            context['is_following'] = Follow.objects.filter(
                follower=current_user,
                following=profile_user
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
            following=target_user
        ).first()
        
        if follow_relation:
            # Unfollow
            follow_relation.delete()
            messages.success(request, f"You have unfollowed {target_user.profile.display_name or target_user.username}.")
        else:
            # Follow
            Follow.objects.create(follower=current_user, following=target_user)
            messages.success(request, f"You are now following {target_user.profile.display_name or target_user.username}!")
        
        return redirect(redirect_url)