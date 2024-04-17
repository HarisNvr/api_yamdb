from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserRegistrationViewSet, TokenObtainView,
                    TitleViewSet, CategoryViewSet, GenreViewSet)

router_v1 = DefaultRouter()
router_v1.register('auth/signup', UserRegistrationViewSet, basename='signup')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('v1/', include('djoser.urls.base')),
]
