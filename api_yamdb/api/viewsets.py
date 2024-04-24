from rest_framework import viewsets, mixins, filters
from rest_framework.pagination import LimitOffsetPagination

from .permission import IsAdminOrReadOnly


class CategoryGenreViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
