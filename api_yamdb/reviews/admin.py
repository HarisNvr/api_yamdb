from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    User, Category, Genre, Title, GenreTitle, Review, Comment
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'last_name', 'email', 'bio', 'role')
    list_filter = ('role',)
    search_fields = ('first_name', 'last_name', 'email')
    list_editable = ('role',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'description', 'year', 'category', 'calculate_rating',
    )
    list_display_links = ('name', 'description', 'year', 'category')
    list_filter = ('category', 'genre')
    search_fields = ('name', 'year')


@admin.register(GenreTitle)
class GenreTitleAdmin(admin.ModelAdmin):
    list_display = ('genre', 'title')
    list_filter = ('genre',)
    search_fields = ('genre__name', 'title__name')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'score', 'pub_date')
    list_filter = ('author', 'score', 'pub_date')
    list_editable = ('score',)
    search_fields = ('title__name', 'text')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'review', 'author', 'pub_date')
    list_filter = ('author', 'pub_date')
    search_fields = ('text', 'review__title__name', 'author__username')
