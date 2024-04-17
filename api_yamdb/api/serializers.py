from datetime import timezone

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Genre, Review, Comment, Title

User = get_user_model()


class CustomUserCreateSerializer(UserSerializer):

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Имя пользователя "me" не допустимо.')
        return value

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('email', 'username')
            ),
        ]


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    slug = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('name', 'slug'),
                message='Категория с таким слагом уже существует.')
        ]


class GenreSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )
    slug = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('name', 'slug'),
                message='Жанр с таким слагом уже существует.')
        ]


class TitleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=256)
    year = serializers.IntegerField()
    rating = serializers.FloatField(source='calculate_rating', read_only=True)
    description = serializers.CharField(max_length=512)
    genre = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        read_only_fields = ('post',)

    def get_genre(self, obj):
        genres = obj.genre.all()
        return [{'name': genre.name, 'slug': genre.slug} for genre in genres]

    def validate_year(self, value):
        current_year = timezone.now().year
        if value <= 0:
            raise serializers.ValidationError(
                'Год создания не может быть отрицательным числом!'
            )
        elif value > current_year:
            raise serializers.ValidationError(
                'Год создания не может быть больше текущего!'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'pub_date')
