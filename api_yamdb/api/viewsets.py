from rest_framework import viewsets, mixins, filters, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .permission import IsAdminOrReadOnly


class CreateDestroyListViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    pass


class CategoryGenreViewSet(CreateDestroyListViewSet):
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def perform_destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        super(CategoryGenreViewSet, self).perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
