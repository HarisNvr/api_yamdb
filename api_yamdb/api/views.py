import random
import string

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (UserCreateSerializer, TitleSerializer,
                          GenreSerializer, CategorySerializer,
                          ReviewSerializer, CommentSerializer,
                          UserCreatАdvancedSerializer, TokenObtainSerializer)
from .permission import (
    IsAdminOrReadOnly, IsAuthorModAdminOrReadOnlyPermission, IsAdmin
)
from .viewsets import CreateDestroyListViewSet
from reviews.models import (
    Title, Category, Genre, Review, Comment, ActivationeCode
)

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


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (IsAuthorModAdminOrReadOnlyPermission,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {"detail": "Метод не разрешен."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)

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

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(
            author=self.request.user,
            review=review
        )

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {"detail": "Метод не разрешен."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        review_id = self.kwargs['review_id']
        queryset = Comment.objects.filter(review_id=review_id)
        return queryset

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

    def retrieve(self, request):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)
