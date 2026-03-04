from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def root_required(view_func):
    """
    Decorator to check if the user is of type 0 (Root).
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 0:
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You don't have permission to access this page.")
    return _wrapped_view