from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, CategoryViewSet, TaskViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', AuthViewSet.as_view({'post': 'list'}), name='login'),
    path('auth/logout/', AuthViewSet.as_view({'post': 'destroy'}), name='logout'),
    path('auth/account/', AuthViewSet.as_view({'get': 'retrieve'}), name='account'),
    path('auth/edit/', AuthViewSet.as_view({'put': 'partial_update'}), name='edit'),
    path('auth/delete_account/', AuthViewSet.as_view({'delete': 'delete'}), name='delete_account'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]