from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BookViewSet, TransactionViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"books", BookViewSet, basename="book")
router.register(r"transactions", TransactionViewSet, basename="transaction")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]