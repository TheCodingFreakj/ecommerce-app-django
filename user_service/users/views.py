# users/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
# Set up logging
logger = logging.getLogger(__name__)
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": "This is a protected view"})
    
class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        logger.info("RegisterView: Received request to register user")
        try:
            response = super().create(request, *args, **kwargs)
            user = response.data
            logger.info(f"RegisterView: User {user['username']} created successfully")
            refresh = RefreshToken.for_user(get_user_model().objects.get(username=user['username']))
            response.data['refresh'] = str(refresh)
            response.data['access'] = str(refresh.access_token)
            logger.info(f"RegisterView: JWT tokens generated for user {user['username']}")
            return response
        except Exception as e:
            logger.error(f"RegisterView: Error occurred - {str(e)}")
            return Response({"error": "Registration failed"}, status=400)


class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("LoginView: Received request to log in user")
        from django.contrib.auth import authenticate

        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            logger.info(f"LoginView: User {username} authenticated successfully")
            refresh = RefreshToken.for_user(user)
            logger.info(f"LoginView: JWT tokens generated for user {username}")
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            logger.warning(f"LoginView: Failed login attempt for username {username}")
            return Response({"error": "Invalid Credentials"}, status=400)

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        user_info = {
            'userid': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            # Include any other user fields you want to return
        }
        return Response(user_info)