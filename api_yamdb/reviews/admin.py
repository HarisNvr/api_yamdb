from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Avg

from .models import (
    User, Category, Genre, Title, Review, Comment
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
        'name', 'description', 'year', 'category', 'calculate_rating', 'genres_display',
    )
    list_display_links = ('name', 'description', 'year', 'category')
    list_filter = ('category', 'genre')
    search_fields = ('name', 'year')

    def genres_display(self, obj):
        return ', '.join(genre.name for genre in obj.genre.all())

    genres_display.short_description = 'Genres'

    def calculate_rating(self, obj):
        return obj.rating

    calculate_rating.short_description = 'Средний рэйтиг'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(rating=Avg('reviews__score'))
        return queryset


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
