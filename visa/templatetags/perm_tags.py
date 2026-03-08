from django import template
from django.contrib.auth import get_user_model

register = template.Library()


@register.filter
def has_perm(user, permission):
    if not user or not user.is_authenticated:
        return False
    try:
        # Assuming your custom user model is named CustomUser
        from visa.models import CustomUser

        # Get the CustomUser instance corresponding to the request.user ID
        custom_user_instance = CustomUser.objects.get(id=user.id)
        # Root user (user_type 0) should have all permissions in the admin panel
        if custom_user_instance.user_type == 0:
            return True
        # For other users, check their explicit permissions
        return user.has_perm(permission)
    except Exception:
        return False
