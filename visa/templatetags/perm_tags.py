from django import template
from django.contrib.auth import get_user_model

register = template.Library()

@register.filter
def has_perm(user, permission):
    try:
        # Assuming your custom user model is named CustomUser
        CustomUser = get_user_model()
        # Get the CustomUser instance corresponding to the request.user ID
        custom_user_instance = CustomUser.objects.get(id=user.id)
        # Check if the user role is 2 (assuming 2 denotes a role needing permission)
        if custom_user_instance.user_type == 0:
            # If the user has the permission, return True, otherwise False
            return user.has_perm(permission)
        else:
            # If the user role is not 2, return True (no permission required)
            return True
    except CustomUser.DoesNotExist:
        # If the CustomUser instance does not exist, return False
        return False