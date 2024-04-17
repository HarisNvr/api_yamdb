from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'email',
        'bio',
        'role',
    )
    list_filter = (
        'role',
    )
    search_fields = (
        'first_name',
        'last_name',
        'email',
    )
