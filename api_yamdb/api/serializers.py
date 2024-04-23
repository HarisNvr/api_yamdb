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


class TokenObtainSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=USERNAME_LEN, write_only=True,
    )
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_LEN, required=True, write_only=True,
    )
    token = serializers.SerializerMethodField()

    def get_token(self, user):
        return str(AccessToken.for_user(user))

    def validate_username(self, value):
        if not User.objects.filter(username=value).exists() and value:
            raise NotFound('Invalid username')
        return value

    def validate_confirmation_code(self, value):
        if not value.isalnum() or len(value) != CONFIRMATION_CODE_LEN:
            raise ValidationError("Invalid confirmation code")
        return value

    def create(self, validated_data):
        user = get_object_or_404(self.Meta.model, **validated_data)
        self.get_token(user)
        user.confirmation_code = None
        user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'confirmation_code', 'token')


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=EMAIL_LEN, required=True,
    )
    username = serializers.CharField(
        max_length=USERNAME_LEN,
        required=True,
        validators=(RegexValidator(
                    regex=r'^[-a-zA-Z0-9_]+$',
                    message='Username может содержать только латинские '
                            'буквы, цифры, дефисы и знаки подчеркивания.'
                    ),)
    )

    def validate_username(self, value):
        if not value:
            raise NotFound()
        if value == 'me':
            raise ValidationError('Имя пользователя "me" не допустимо.')
        return value

    def validate(self, attrs):
        if self.Meta.model.objects.filter(
            username=attrs.get('username')
        ).exists() != self.Meta.model.objects.filter(
            email=attrs.get('email')
        ).exists():
            raise ValidationError('Данные не валидны')
        return attrs

    def create(self, validated_data):
        instance, _ = self.Meta.model.objects.get_or_create(**validated_data)
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

    class Meta:
        model = User
        fields = ('email', 'username')


class UserCreatAdvancedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'bio', 'role'
        )


class UserProfileSerializer(UserCreatAdvancedSerializer):
    class Meta(UserCreatAdvancedSerializer.Meta):
        read_only_fields = ('role',)


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
        read_only_fields = ('author',)

    def validate(self, data):
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        author = self.context['request'].user

        if not self.instance:
            if Review.objects.filter(title=title, author=author).exists():
                raise serializers.ValidationError(
                    'Вы уже написали обзор на это произведение.'
                )

        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
