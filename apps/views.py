from datetime import date
from django.contrib.auth import logout
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import permission_classes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from apps.models import Category, Task
from apps.serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer, CategorySerializer, TaskSerializer
from apps.throttling import AnonDailyThrottle, UserDailyThrottle


class AuthViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    throttle_classes = [AnonDailyThrottle, UserDailyThrottle]

    def get_permissions(self):
        if self.action in ['register', 'login']:
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

    @extend_schema(tags=['auth'], operation_id='auth_register')
    def create(self, request):  # POST /api/v1/auth/ - Register
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(tags=['auth'], operation_id='auth_login')
    def list(self, request):  # POST /api/v1/auth/login/ - Login
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(tags=['auth'], operation_id='auth_logout')
    def destroy(self, request):  # POST /api/v1/auth/logout/
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(tags=['user'], operation_id='user_retrieve')
    def retrieve(self, request):  # GET /api/v1/auth/account/ - Account/About
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(tags=['user'], operation_id='user_update')
    def partial_update(self, request):  # PUT /api/v1/auth/edit/ - Edit user
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(tags=['user'], operation_id='user_delete')
    def delete(self, request):  # DELETE /api/v1/auth/delete_account/
        request.user.delete()
        return Response({"message": "Account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class CategoryViewSet(GenericViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        query = self.request.query_params.get('search', '')
        return Category.objects.filter(user=self.request.user, title__icontains=query)

    @extend_schema(tags=['category'], operation_id='category_list')
    def list(self, request, *args, **kwargs):  # GET /api/v1/categories/ - Category list & Search
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['category'], operation_id='category_create')
    def create(self, request, *args, **kwargs):  # POST /api/v1/categories/ - Add category
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['category'],
        operation_id='category_retrieve',
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH)
        ]
    )
    def retrieve(self, request, pk=None):  # GET /api/v1/categories/<id>/ - About category
        return super().retrieve(request, pk=pk)

    @extend_schema(
        tags=['category'],
        operation_id='category_update',
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH)
        ]
    )
    def update(self, request, pk=None):  # PUT /api/v1/categories/<id>/ - Update category
        return super().update(request, pk=pk)

    @extend_schema(
        tags=['category'],
        operation_id='category_delete',
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH)
        ]
    )
    def destroy(self, request, pk=None):  # DELETE /api/v1/categories/<id>/ - Delete category
        return super().destroy(request, pk=pk)

class TaskViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        query = self.request.query_params.get('search', '')
        filter_type = self.request.query_params.get('filter', 'all')

        tasks = Task.objects.filter(user=self.request.user)
        if query:
            tasks = tasks.filter(Q(title__icontains=query) | Q(category__title__icontains=query))

        if filter_type == 'today':
            tasks = tasks.filter(due_date=date.today())
        elif filter_type == 'last':
            tasks = tasks.filter(due_date__lt=date.today())

        return tasks

    @extend_schema(tags=['tasks'], operation_id='task_list')
    def list(self, request, *args, **kwargs):  # GET /api/v1/tasks/ - All tasks, Today tasks, Last tasks & Search
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['tasks'], operation_id='task_create')
    def create(self, request, *args, **kwargs):  # POST /api/v1/tasks/ - Add task
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)