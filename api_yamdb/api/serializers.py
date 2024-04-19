from datetime import datetime as dt

from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from reviews.models import (
    Category, Genre, Review, Comment, Title, ActivationeCode
)

User = get_user_model()


class TokenObtainSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    def validate_user(self, value):
        if not User.objects.filter(username=value).exists() and value:
            raise serializers.ValidationError('Неподходящий username')
        return value

    class Meta:
        model = ActivationeCode
        fields = ('user', 'confirmation_code')


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


class CategorySerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=256)
    slug = serializers.CharField(max_length=16, validators=[
        RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Слаг может содержать только латинские '
                    'буквы, цифры, дефисы и знаки подчеркивания.'
        ),
        UniqueValidator(
            queryset=Genre.objects.all()
        )
    ])

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=256)
    year = serializers.IntegerField()
    rating = serializers.FloatField(source='calculate_rating', read_only=True)
    description = serializers.CharField(max_length=512)
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def create(self, validated_data):
        genres_data = validated_data.pop('genre', [])
        title = Title.objects.create(**validated_data)

        for genre in genres_data:
            title.genre.add(genre)

        return title

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategorySerializer(instance.category).data
        representation['genre'] = GenreSerializer(instance.genre.all(),
                                                  many=True).data
        return representation

    def get_genre(self, obj):
        genres = obj.genre.all()
        return [{'name': genre.name, 'slug': genre.slug} for genre in genres]

    def validate_year(self, value):
        current_year = dt.now().year
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
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
