from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
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
    IsAdminOrReadOnly, IsAuthorModAdminOrReadOnlyPermission, IsAdmin
)
from .viewsets import CreateDestroyListViewSet
from reviews.models import (
    Title, Category, Genre, Review, Comment, User
)


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
