import random
import string

from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import (
    Category, Genre, Review, Comment, Title, User
)
from reviews.constants import EMAIL_LEN, CONFIRMATION_CODE_LEN, USERNAME_LEN
from reviews.mixins import UsernameValidatorMixin


class TokenObtainSerializer(
    serializers.Serializer, UsernameValidatorMixin
):
    username = serializers.CharField(
        max_length=USERNAME_LEN,
        required=True,
        write_only=True,
    )
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_LEN, required=True, write_only=True,
    )

    class Meta:
        fields = ('username', 'confirmation_code')

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists() and value:
            raise NotFound('Invalid username')
        return UsernameValidatorMixin.validate_username(self, value)

    def validate_confirmation_code(self, value):
        if not value.isalnum() or len(value) != CONFIRMATION_CODE_LEN:
            raise ValidationError('Invalid confirmation code')
        return value

    def create(self, validated_data):
        user = get_object_or_404(User, **validated_data)
        return AccessToken.for_user(user)


class UserCreateSerializer(
    serializers.Serializer, UsernameValidatorMixin
):
    email = serializers.EmailField(
        max_length=EMAIL_LEN, required=True,
    )
    username = serializers.CharField(
        max_length=USERNAME_LEN,
        required=True,
    )

    class Meta:
        fields = ('email', 'username')

    def validate(self, attrs):
        if User.objects.filter(**attrs):
            return attrs
        if User.objects.filter(
            username=attrs.get('username')
        ).exists() or User.objects.filter(
            email=attrs.get('email')
        ).exists():
            raise ValidationError('Данные не валидны')
        return attrs

    def create(self, validated_data):
        instance, _ = User.objects.get_or_create(**validated_data)
        confirmation_code = self.generate_confirmation_code()
        instance.confirmation_code = confirmation_code
        instance.save()
        self.send_confirmation_email(validated_data.get('email'),
                                     confirmation_code)
        return instance

    def generate_confirmation_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits,
                                      k=CONFIRMATION_CODE_LEN))

    def send_confirmation_email(self, email, confirmation_code):
        subject = 'Код подтверждения регистрации на YaMDB'
        message = f'Ваш код подтверждения: {confirmation_code}'
        from_email = None
        recipient_list = (email,)
        send_mail(subject, message, from_email, recipient_list)


class UserCreatAdvancedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'bio', 'role'
        )


class UserProfileSerializer(UserCreatAdvancedSerializer):
    class Meta(UserCreatAdvancedSerializer.Meta):
        read_only_fields = ('role',)


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
    rating = serializers.IntegerField(read_only=True)
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
