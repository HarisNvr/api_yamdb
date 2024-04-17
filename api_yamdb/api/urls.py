from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationViewSet, TokenObtainView

router_v1 = DefaultRouter()
router_v1.register('auth/signup', UserRegistrationViewSet, basename='signup')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', TokenObtainView.as_view(), name='token_obtain'),
    path('v1/', include('djoser.urls.base')),
]
