from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiTypes
from .serializers import (
    UserSerializer, UserCreateSerializer, 
    UserUpdateSerializer, ChangePasswordSerializer, UserLoginSerilazers
)
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserLoginSerilazers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        tokens = serializer.validated_data

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": getattr(user, 'role', ''),
            },
            "tokens": {
                "access": tokens['access'],
                "refresh": tokens['refresh'],
            }
        })




class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user.
    
    POST /api/users/register/
    {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe",
        "role": "viewer",
        "company": "Acme Corp"
    }
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"New user registered: {user.username}")
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update current user profile.
    
    GET /api/users/profile/
    PUT /api/users/profile/
    PATCH /api/users/profile/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        logger.info(f"User profile updated: {instance.username}")
        
        return Response({
            'user': UserSerializer(instance).data,
            'message': 'Profile updated successfully'
        })


class ChangePasswordView(APIView):
    """
    Change user password.
    
    POST /api/users/change-password/
    {
        "old_password": "OldPass123!",
        "new_password": "NewPass123!",
        "new_password_confirm": "NewPass123!"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=ChangePasswordSerializer,
        responses=OpenApiTypes.OBJECT,
        summary="Change password"
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            logger.info(f"Password changed for user: {request.user.username}")
            
            return Response({
                'message': 'Password changed successfully. Please login again.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    Logout user by blacklisting refresh token.
    
    POST /api/users/logout/
    {
        "refresh": "refresh_token_here"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=OpenApiTypes.OBJECT,
        responses=OpenApiTypes.OBJECT,
        summary="User logout"
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info(f"User logged out: {request.user.username}")
            
            return Response({
                "message": "Successfully logged out"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserListView(generics.ListAPIView):
    """
    List all users (admin only).
    
    GET /api/users/list/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only admins can list all users
        if not self.request.user.is_admin:
            return User.objects.filter(id=self.request.user.id)
        
        queryset = User.objects.all()
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Search by username or email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )
        
        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a specific user (admin only).
    
    GET /api/users/<id>/
    PUT /api/users/<id>/
    DELETE /api/users/<id>/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Admins can access all users, others only themselves
        if self.request.user.is_admin:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    def destroy(self, request, *args, **kwargs):
        # Only admins can delete users
        if not request.user.is_admin:
            return Response(
                {"error": "Only admins can delete users"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        
        # Prevent self-deletion
        if user.id == request.user.id:
            return Response(
                {"error": "You cannot delete your own account"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = user.username
        self.perform_destroy(user)
        
        logger.info(f"User deleted: {username} by {request.user.username}")
        
        return Response(
            {"message": f"User {username} deleted successfully"},
            status=status.HTTP_200_OK
        )


class PromoteUserView(APIView):
    """
    Promote a user to admin or analyst role (admin only).
    
    POST /api/users/promote/
    {
        "user_id": 1,
        "role": "admin"  // or "analyst"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=OpenApiTypes.OBJECT,
        responses=OpenApiTypes.OBJECT,
        summary="Promote user role (admin only)"
    )
    def post(self, request):
        # Only admins can promote users
        if not request.user.is_admin:
            return Response(
                {"error": "Only admins can promote users"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        new_role = request.data.get('role')
        
        if not user_id or not new_role:
            return Response(
                {"error": "user_id and role are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate role
        valid_roles = ['admin', 'analyst', 'viewer']
        if new_role not in valid_roles:
            return Response(
                {"error": f"Invalid role. Must be one of: {', '.join(valid_roles)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent self-demotion from admin
        if user_id == request.user.id and new_role != 'admin':
            return Response(
                {"error": "You cannot demote yourself from admin"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            old_role = user.role
            user.role = new_role
            user.save()
            
            logger.info(
                f"User {user.username} promoted from {old_role} to {new_role} "
                f"by {request.user.username}"
            )
            
            return Response({
                'message': f'User {user.username} promoted to {new_role}',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class DemoteUserView(APIView):
    """
    Demote a user from admin role (admin only).
    
    POST /api/users/demote/
    {
        "user_id": 1,
        "role": "analyst"  // or "viewer" - cannot be "admin"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=OpenApiTypes.OBJECT,
        responses=OpenApiTypes.OBJECT,
        summary="Demote user from admin (admin only)"
    )
    def post(self, request):
        # Only admins can demote users
        if not request.user.is_admin:
            return Response(
                {"error": "Only admins can demote users"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        new_role = request.data.get('role', 'viewer')
        
        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate role - cannot demote to admin
        valid_roles = ['analyst', 'viewer']
        if new_role not in valid_roles:
            return Response(
                {"error": f"Invalid role for demotion. Must be one of: {', '.join(valid_roles)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent self-demotion
        if user_id == request.user.id:
            return Response(
                {"error": "You cannot demote yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            
            # Check if user is actually an admin
            if user.role != 'admin':
                return Response(
                    {"error": f"User {user.username} is not an admin (current role: {user.role})"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            old_role = user.role
            user.role = new_role
            user.save()
            
            logger.info(
                f"User {user.username} demoted from {old_role} to {new_role} "
                f"by {request.user.username}"
            )
            
            return Response({
                'message': f'User {user.username} demoted from admin to {new_role}',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )