import random
import string

from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import LimitOffsetPagination

from .serializers import (CustomUserCreateSerializer, TitleSerializer,
                          GenreSerializer, CategorySerializer)
from .permission import IsAdminOrReadOnly
from .viewsets import CreateDestroyListViewSet
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


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_slug = self.request.query_params.get('genre', None)
        category_slug = self.request.query_params.get('category', None)
        title_year = self.request.query_params.get('year', None)
        title_name = self.request.query_params.get('name', None)
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        elif category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        elif title_year:
            queryset = queryset.filter(year=title_year)
        elif title_name:
            queryset = queryset.filter(name=title_name)
        return queryset

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {"detail": "Метод не разрешен."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)


class CategoryViewSet(CreateDestroyListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def perform_destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        super(CategoryViewSet, self).perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(CreateDestroyListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def perform_destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        super(GenreViewSet, self).perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
