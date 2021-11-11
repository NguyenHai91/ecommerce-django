
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User

# Register your models here.

# class UserAdmin(UserAdmin):
#   list_display = ['email', 'first_name', 'last_name', 'phone', 'last_login', 'create_date', 'is_active']
#   filter_horizontal = ()
#   list_filter = ()
#   fieldsets = ()

admin.site.register(User)