import datetime
import logging
import os
from pathlib import Path
import requests
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class RequestTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = datetime.now()
        response = self.get_response(request)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000
        logger.info(f"Request to {request.path} took {duration} ms")
        return response    


from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
class SetLastModifiedBy:
    def __init__(self, func):
        self.func = func

    async def __call__(self, viewset_instance, request, *args, **kwargs):
        logger.info(f"Intercepting the request at the __call__----------------> {self}")
        logger.info(f"Intercepting the request at the viewset_instance----------------> {viewset_instance}")
        logger.info(f"Intercepting the request at the request----------------> {request}")
        token = request.headers.get('Authorization')
        logger.info(f"Authorization Information ------------------> {token}")
        user_id = self.get_user_id_from_auth_service(token)
        if user_id:
            request.data['last_modified_by'] = user_id
        else:
            return Response({"detail": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        return self.func(viewset_instance, request, *args, **kwargs)

    async def get_user_id_from_auth_service(self, token):
        try:
            response = requests.get(f"{os.environ.get('AUTH_SERVICE_URL')}/user-info", headers={'Authorization': f'Bearer {token}'})
            if response.status_code == 200:
                return response.json().get('userid')
            else:
                return None
        except Exception as e:
            return None