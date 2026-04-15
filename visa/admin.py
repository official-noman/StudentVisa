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
admin.site.register(TopConsultant)
admin.site.register(CountryAdds)
admin.site.register(CountryWises)
admin.site.register(Customizes)
admin.site.register(Users)
admin.site.register(Students)


class VisaServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_active',)
    search_fields = ('title',)

admin.site.register(VisaService, VisaServiceAdmin)