from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
import random
import string

from .serializers import CustomUserCreateSerializer
from .permission import IsAuthorModerAdminOrReadOnly

User = get_user_model()

from djoser.views import UserViewSet 


class UserRegistrationViewSet(viewsets.GenericViewSet):
    serializer_class = CustomUserCreateSerializer
    queryset = User.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get('email')
        #if not User.objects.filter(**request.data).exists:
        #    serializer.save()
        # Генерация и отправка кода подтверждения
        confirmation_code = self.generate_confirmation_code()
        self.send_confirmation_email(email, confirmation_code)
        #user = get_object_or_404(User, username=request.data.get('username'))
        return Response(request.data, status=status.HTTP_200_OK)

    def generate_confirmation_code(self):
        # Генерация случайного кода подтверждения
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def send_confirmation_email(self, email, confirmation_code):
        # Отправка письма с кодом подтверждения на указанный email
        subject = 'Код подтверждения регистрации на YaMDB'
        message = f'Ваш код подтверждения: {confirmation_code}'
        from_email = 'noreply@example.com'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)


class TokenObtainView(APIView):
    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        # Проверяем, существует ли пользователь с указанным username
        user = authenticate(username=username, confirmation_code=confirmation_code)
        if not user:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Если пользователь найден, создаем JWT-токен
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)

        return Response({"token": token}, status=status.HTTP_200_OK)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = IsAuthorModerAdminOrReadOnly
