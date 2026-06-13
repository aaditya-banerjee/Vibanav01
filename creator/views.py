from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from store.models import DesignSubmission
from .forms import DesignSubmissionForm
from django.contrib.auth import login, logout, authenticate

# Create your views here.
@login_required
def creator_portal(request):
    # 1. Handle new artwork submissions
    if request.method == 'POST':
        # Notice we include request.FILES because this form handles images!
        form = DesignSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            # Pause the save so we can attach the logged-in user as the designer
            submission = form.save(commit=False)
            submission.designer = request.user
            submission.save()
            messages.success(request, "Artwork submitted successfully! Our team will review it shortly.")
            return redirect('store:creator_portal')
    else:
        form = DesignSubmissionForm()

    # 2. Fetch the designer's history to display on the dashboard
    past_submissions = DesignSubmission.objects.filter(designer=request.user).order_by('-submitted_at')

    context = {
        'form': form,
        'past_submissions': past_submissions
    }
    return render(request, 'store/creator_portal.html', context)

def custom_login(request):
    # Check 1: If they are already logged in, send them to the right place
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('admin:index')
        return redirect('creator:portal') # Fixed namespace!

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Check 2: Route them after a successful login
            if user.is_superuser or user.is_staff:
                messages.success(request, f"Welcome back to the Admin Dashboard, {user.username}!")
                return redirect('admin:index')
            else:
                messages.success(request, f"Welcome to your Creator Workspace, {user.username}!")
                return redirect('creator:portal') # Fixed namespace!
    else:
        form = AuthenticationForm()
        
    return render(request, 'store/login.html', {'form': form})


# NEW: A clean, universal logout view
def custom_logout(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('store:catalog') # Always send them back to the shop