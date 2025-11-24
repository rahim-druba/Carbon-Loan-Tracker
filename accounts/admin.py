from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'city', 'is_staff')
    list_filter = ('role', 'city', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile Info', {'fields': ('role', 'date_of_birth', 'city', 'national_id', 'avatar')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile Info', {'fields': ('role', 'date_of_birth', 'city', 'national_id', 'avatar')}),
    )
