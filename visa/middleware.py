from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from .models import UserSession
from django.contrib.auth import logout

class RedirectIfLoggedInMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.path in [reverse('login_user'), reverse('login_student'), reverse('signup_user'), reverse('signup_student'), reverse('redirect_to_otp'), reverse('otp_verification_signup'), reverse('otp_verification_signup_student')]:
                return redirect('home')
            
        response = self.get_response(request)

        return response
        
    
class SessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the session has a last activity time
        if 'last_activity_time' in request.session:
            last_activity_time = datetime.fromisoformat(request.session['last_activity_time'])
            current_time = timezone.now()

            # Calculate the elapsed time since the last activity
            elapsed_time = (current_time - last_activity_time).total_seconds()

            # Check if the elapsed time exceeds the expiration time (e.g., 10 minutes)
            expiration_time_seconds = 300  # 5 minutes
            if elapsed_time > expiration_time_seconds:
                # Destroy the session
                # request.session.flush()
                del request.session['next_page']
                del request.session['last_activity_time']
                request.session.modified = True
            # else:
            #     # Update the last activity time
            #     request.session['last_activity_time'] = current_time.isoformat()

        # Process the request
        response = self.get_response(request)

        return response
    
class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if the user is authenticated and has an active session
        if request.user.is_authenticated:
            user_session = UserSession.objects.filter(user=request.user, end_time__isnull=True).first()
            if user_session:
                # Check if there has been no activity for the last 3 minutes
                last_activity_time = user_session.end_time
                current_time = timezone.now()
                if (current_time - last_activity_time).total_seconds() > 3600:
                    # Log out the user
                    logout(request)
                    return redirect('home')  # Redirect to the home page after logout
        
        return response
