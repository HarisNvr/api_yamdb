from datetime import datetime as dt

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from reviews.models import (
    Category, Genre, Review, Comment, Title
)

User = get_user_model()


class TokenObtainSerializer(serializers.ModelSerializer):
    username = serializers.SlugRelatedField(
        slug_field='user.username', read_only=True
    )

    def validate_user(self, value):
        if not User.objects.filter(username=value).exists() and value:
            raise serializers.ValidationError('Неподходящий username')
        return value

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserCreateSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Имя пользователя "me" не допустимо.')
        return value

    class Meta:
        fields = ('email', 'username')
        model = User


class UserCreatАdvancedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'bio', 'role'
        )

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user.role == 'admin':
            return super().update(instance, validated_data)
        validated_data.pop('role', None)
        return super().update(instance, validated_data)


class CategoryGenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=256)
    slug = serializers.CharField(max_length=16, validators=[
        RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Слаг может содержать только латинские '
                    'буквы, цифры, дефисы и знаки подчеркивания.'
        ),
        UniqueValidator(
            queryset=Category.objects.all()
        )
    ])


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='calculate_rating',
        read_only=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True,
        allow_null=False,
        allow_empty=False
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category).data
        representation['genre'] = GenreSerializer(instance.genre.all(),
                                                  many=True).data
        return representation


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
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
