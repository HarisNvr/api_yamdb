from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserRegistrationViewSet, TokenObtainView,
                    TitleViewSet, CategoryViewSet, GenreViewSet,
                    ReviewViewSet, CommentViewSet, CustomUserViewSet,
                    UserProfileAPIView)

router_v1 = DefaultRouter()
router_v1.register(r'auth/signup', UserRegistrationViewSet, basename='signup')
router_v1.register(r'titles', TitleViewSet, basename='titles')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews',
                   ReviewViewSet, basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('v1/categories/<slug:slug>/',
         CategoryViewSet.as_view({'delete': 'perform_destroy'}),
         name='category-destroy'),
    path('v1/genres/<slug:slug>/',
         GenreViewSet.as_view({'delete': 'perform_destroy'}),
         name='genre-destroy'),
    path('v1/users/me/', UserProfileAPIView.as_view(), name='me'),
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', TokenObtainView.as_view(), name='token_obtain'),
]
