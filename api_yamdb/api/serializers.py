from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from rest_framework import serializers
User = get_user_model()
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from reviews.models import ActivationeCode, CustomUser
from django.http import Http404

class TokenObtainSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    def validate_user(self, value):
        if not User.objects.filter(username=value).exists() and value:
            raise serializers.ValidationError("Email обязателен для заполнения.", code='existing_username')
        return value

    class Meta:
        model = ActivationeCode
        fields = ('user', 'confirmation_code')


class UserCreateSerializer(UserSerializer):

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError('Имя пользователя "me" не допустимо.')
        return value

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username')
        model = User


class UserCreatАdvancedSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'bio', 'role')

    def validate_username(self, value):
        if value == 'me' and len(value) <= 150:
            raise ValidationError('Имя пользователя "me" не допустимо.')
        return value
