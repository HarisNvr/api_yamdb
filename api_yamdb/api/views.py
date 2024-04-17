import random
import string

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import LimitOffsetPagination

from .serializers import CustomUserCreateSerializer, TitleSerializer
from .permission import IsAuthorModerAdminOrReadOnly, IsAdmin
from .viewsets import CreateListViewSet
from reviews.models import Title, Category, Genre

User = get_user_model()


class UserRegistrationViewSet(viewsets.GenericViewSet):
    serializer_class = CustomUserCreateSerializer
    queryset = User.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get('email')
        confirmation_code = self.generate_confirmation_code()
        self.send_confirmation_email(email, confirmation_code)
        return Response(request.data, status=status.HTTP_200_OK)

    def generate_confirmation_code(self):
        return ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=6)
        )

    def send_confirmation_email(self, email, confirmation_code):
        subject = 'Код подтверждения регистрации на YaMDB'
        message = f'Ваш код подтверждения: {confirmation_code}'
        from_email = 'noreply@example.com'
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)


class TokenObtainView(APIView):
    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        user = authenticate(username=username,
                            confirmation_code=confirmation_code)
        if not user:
            return Response(
                {"error": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)

        return Response({"token": token}, status=status.HTTP_200_OK)


class TitleViewSet(CreateListViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorModerAdminOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CategoryViewSet(CreateListViewSet):
    queryset = Category.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdmin,)


class GenreViewSet(CreateListViewSet):
    queryset = Genre.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdmin,)
