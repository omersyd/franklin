from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from .forms import UserRegistrationForm, UserProfileForm
from .models import CustomUser


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
        'title': 'Create Account'
    }
    return render(request, 'accounts/register.html', context)


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'Welcome back, {username}!')
                next_page = request.GET.get('next', 'status')
                return redirect(next_page)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')

    form = AuthenticationForm()
    context = {
        'form': form,
        'title': 'Login'
    }
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('status')


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    context = {
        'form': form,
        'title': 'My Profile',
        'user': request.user
    }
    return render(request, 'accounts/profile.html', context)
