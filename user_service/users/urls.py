# users/urls.py
from django.urls import path
from .views import ProtectedView, RegisterView, LoginView, UserInfoView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('user-info/', UserInfoView.as_view(), name='user-info'),
]
