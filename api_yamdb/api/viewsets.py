from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins

from .permission import IsAuthorModerAdminOrReadOnly
from djoser.views import UserViewSet


class CreateDestroyListViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    pass


class RetrieveCreateDestroyListViewSet(
    mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    pass


class CustomUserViewSet(UserViewSet):
    User = get_user_model()
    queryset = User.objects.all()
    permission_classes = IsAuthorModerAdminOrReadOnly
