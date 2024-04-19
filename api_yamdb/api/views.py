import random
import string

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserCreateSerializer, UserCreatАdvancedSerializer, TokenObtainSerializer
)
from .permission import IsAdmin
from reviews.models import ActivationeCode

User = get_user_model()


class UserRegistrationViewSet(viewsets.GenericViewSet):
    def create(self, request):
        email = request.data.get('email')
        if not User.objects.filter(username=request.data.get('username'),
                                   email=email).exists():
            serializer = UserCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        confirmation_code = self.generate_confirmation_code()
        ActivationeCode.objects.update_or_create(
            user=User.objects.get(username=request.data.get('username')),
            defaults={'confirmation_code': confirmation_code},
        )
        self.send_confirmation_email(email,
                                     confirmation_code)
        return Response(request.data, status=status.HTTP_200_OK)

    def generate_confirmation_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits,
                                      k=6))

    def send_confirmation_email(self, email, confirmation_code):
        subject = 'Код подтверждения регистрации на YaMDB'
        message = f'Ваш код подтверждения: {confirmation_code}'
        from_email = 'noreply@example.com'
        recipient_list = (email,)
        send_mail(subject, message, from_email, recipient_list)


class TokenObtainView(APIView):
    def post(self, request):
        username = User.objects.filter(
            username=request.data.get('username')
        ).exists()
        if request.data.get('username') and not username:
            return Response({'error': 'username отсутсвует в бд'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not ActivationeCode.objects.filter(**serializer.data).exists():
            return Response({'error': 'Данные не верны'},
                            status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(username=request.data.get('username'))
        token = str(refresh.access_token)
        return Response({'token': token}, status=status.HTTP_200_OK)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsAdmin)
    serializer_class = UserCreatАdvancedSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'delete', 'patch')


class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserCreatАdvancedSerializer
    http_method_names = ('get', 'patch', 'post')

    def get_queryset(self):
        return User.objects.filter(username=self.request.user.username)

    def list(self, request):
        user = request.user
        serializer = UserCreatАdvancedSerializer(user)
        return Response(serializer.data)
