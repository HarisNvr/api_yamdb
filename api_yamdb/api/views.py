from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from .serializers import (UserCreateSerializer, TitleSerializer,
                          GenreSerializer, CategorySerializer,
                          ReviewSerializer, CommentSerializer,
                          UserCreatAdvancedSerializer, TokenObtainSerializer,
                          UserProfileSerializer,)
from .permission import (
    IsAdminOrReadOnly,
    IsAuthorModAdminOrReadOnlyPermission,
    IsAdmin
)
from .viewsets import CategoryGenreViewSet
from reviews.constants import ALLOWED_METHODS
from reviews.models import (
    Title, Category, Genre, Review, User
)
from .filters import TitleFilter


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenObtainView(APIView):
    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ALLOWED_METHODS
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter


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
    serializer_class = UserCreatAdvancedSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post', 'delete', 'patch')

    def get_permissions(self):
        if self.request.path.endswith('/me/'):
            return (IsAuthenticated(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.path.endswith('/me/'):
            return UserProfileSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=('get',))
    def me(self, request):
        return Response(self.get_serializer(request.user).data)

    @me.mapping.patch
    def patch_me(self, request):
        serializer = self.get_serializer(request.user,
                                         data=request.data,
                                         partial=True,)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @me.mapping.post
    def post_me(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
