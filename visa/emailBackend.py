from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.backends import ModelBackend
from .models import Students, Users




class EmailBackend(ModelBackend):
    def authenticate(self, request=None, email=None, password=None, phone=None, user_type=None, **kwargs):
        UserModel = get_user_model()

        try:
            if email:
                user = UserModel.objects.get(email=email, user_type=user_type)
            elif phone:
                user = UserModel.objects.get(phone=phone, user_type=user_type)
            else:
                return None

            if user.check_password(password):
                return user
            else:
                return None

        except UserModel.DoesNotExist:
            return None