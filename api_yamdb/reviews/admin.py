# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'firsr_name',
        'last_name',
        'email',
        'bio',
        'role',
    )
    list_filter = (
        'role',
    )
    search_fields = (
        'firsr_name',
        'last_name',
        'email',
    )
