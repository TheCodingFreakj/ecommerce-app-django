from django.urls import path
from .views import RegisterView, LoginView, ProtectedView, UserInfoView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('userinfo/', UserInfoView.as_view(), name='userinfo'),
]
