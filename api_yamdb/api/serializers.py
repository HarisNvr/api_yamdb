from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator


class CustomUserCreateSerializer(UserSerializer):

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError("Имя пользователя 'me' не допустимо.")
        return value

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'username')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('email', 'username')
            ),
        ]
