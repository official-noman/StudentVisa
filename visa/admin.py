from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin


# get_user_model = CustomUser

# class CustomUserAdmin(UserAdmin):
#     list_display = ('id', 'email')

# admin.site.register(CustomUser, UserAdmin)
admin.site.register(Addresses)
admin.site.register(Balances)
admin.site.register(ConsultantDetails)
admin.site.register(ConsultantImages)
admin.site.register(ConsultantWises)
admin.site.register(Countries)
admin.site.register(CountryAdds)
admin.site.register(CountryWises)
admin.site.register(Customizes)
admin.site.register(Users)
admin.site.register(Students)