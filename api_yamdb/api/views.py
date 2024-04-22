import random
import string

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken

from .serializers import (UserCreateSerializer, TitleSerializer,
                          GenreSerializer, CategorySerializer,
                          ReviewSerializer, CommentSerializer,
                          UserCreatАdvancedSerializer, TokenObtainSerializer)
from .permission import (
    IsAdminOrReadOnly,
    IsAuthorModAdminOrReadOnlyPermission,
    IsAdmin
)
from .viewsets import CategoryGenreViewSet
from reviews.constants import ALLOWED_METHODS
from reviews.models import (
    Title,
    Category,
    Genre,
    Review,
    Comment
)

User = get_user_model()


class UserRegistrationViewSet(viewsets.GenericViewSet):
    def create(self, request):
        email = request.data.get('email')
        username = request.data.get('username')
        if not User.objects.filter(username=username,
                                   email=email).exists():
            serializer = UserCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        confirmation_code = self.generate_confirmation_code()
        user = User.objects.get(username=username)
        user.confirmation_code = confirmation_code
        user.save()
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
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')
        user = User.objects.filter(username=username)
        print(username)
        print(serializer.data)
        if username and not user.exists():
            return Response({'error': 'username отсутсвует в бд'},
                            status=status.HTTP_404_NOT_FOUND)
        if not User.objects.filter(**serializer.data).exists():
            return Response({'error': 'Данные не верны'},
                            status=status.HTTP_400_BAD_REQUEST)
        token = str(AccessToken.for_user(user.first()))
        return Response({"token": token},
                        status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ALLOWED_METHODS

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


class CategoryViewSet(CategoryGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (IsAuthorModAdminOrReadOnlyPermission,)
    http_method_names = ALLOWED_METHODS

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        if title.reviews.filter(author=self.request.user).exists():
            raise ValidationError(
                'Вы уже оставили отзыв на это произведение.',
                code=400
            )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModAdminOrReadOnlyPermission,)
    http_method_names = ALLOWED_METHODS

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs['review_id'],
            title=get_object_or_404(
                Title,
                pk=self.kwargs.get('title_id')
            )
        )
        serializer.save(
            author=self.request.user,
            review=review
        )

    def get_queryset(self):
        review = Review.objects.get(id=self.kwargs['review_id'])
        return review.commentaries.all()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsAdmin)
    serializer_class = UserCreatАdvancedSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'delete', 'patch')


class UserProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(UserCreatАdvancedSerializer(request.user).data)

    def patch(self, request):
        serializer = UserCreatАdvancedSerializer(request.user,
                                                 data=request.data,
                                                 partial=True,
                                                 context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def post(self, request):
        serializer = UserCreatАdvancedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
