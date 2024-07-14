import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

UserModel = get_user_model()

class ExternalServiceBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # URL of the external authentication service
        auth_url = settings.EXTERNAL_AUTH_URL
        
        # Call the external service
        response = requests.post(auth_url, data={'username': username, 'password': password})

        if response.status_code == 200:
            data = response.json()
            user_id = data.get('user_id')
            email = data.get('email')
            
            # Get or create the user in the Django database
            user, created = UserModel.objects.get_or_create(id=user_id, defaults={'email': email})
            
            if not created:
                # Update user info if needed
                user.email = email
                user.save()
                
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
