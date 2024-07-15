import asyncio
import json
import logging
from aiohttp import ClientSession, ClientConnectorError, ClientTimeout
from django.conf import settings
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import AnonymousUser, User
from asgiref.sync import sync_to_async,async_to_sync
import requests
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
logger = logging.getLogger(__name__)

async def fetch_auth_data(auth_url, headers):
    async with ClientSession() as session:
        async with session.get(auth_url, headers=headers) as response:
            status_code = response.status
            response_text = await response.text()
            try:
                auth_data = await response.json()
            except json.JSONDecodeError:
                auth_data = None
            return auth_data, status_code, response_text
class CustomUser:
    def __init__(self, id, username):
        self.id = id
        self.username = username

    
    @property
    def usrId(self):
        return self.id



class CustomExternalServiceAuthentication(JWTAuthentication):
    def authenticate(self, request):
        logger.debug("CustomExternalServiceAuthentication called for %s", request.path)

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.warning("No Authorization header provided.")
            raise AuthenticationFailed('Authorization header required.')

        auth_url = settings.EXTERNAL_AUTH_URL # Replace with your actual external service URL
        headers = {'Authorization': auth_header}

        try:
            response = requests.get(auth_url, headers=headers)
            status_code = response.status_code
            auth_data = response.json()

            if status_code == 200 and auth_data:
                user_id = auth_data.get('userid')
                username = auth_data.get('username')
              
                logger.debug(f"User {username} Authorized successfully.")
                return (user_id,None)
            else:
                logger.error(f"Failed to authenticate with external service: {status_code} {auth_data}")
                raise AuthenticationFailed('Invalid token.')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with authentication service: {e}")
            raise AuthenticationFailed('Error communicating with authentication service.')

    
class AuthMixin:

    async def authenticate_async(self, request):
        logger.info(f"Adding Debugging Logs..................................")
        auth_header = request.headers.get('Authorization')
        logger.info(f"Adding Debugging Logs..................................{auth_header}")
        if not auth_header:
            logger.warning("No Authorization header provided.")
            return self.create_response({'detail': 'Authorization header required.'}, status=401)

        auth_url = settings.EXTERNAL_AUTH_URL
        logger.info(f"Attempting to connect to auth service at {auth_url}")

        try:
            auth_data, status_code, response_text = await fetch_auth_data(auth_url, {'Authorization': auth_header})
            logger.info(f"Retrieving the authData: {status_code}---->{auth_data}----> {response_text}")
            if status_code == 200 and auth_data:
                user_id = auth_data.get('userid')
                username = auth_data.get('username')
                # Create a simple user object for request context, without saving to DB
               
                logger.debug(
                    f"Retrieving Django Backend -------->  {user_id} created successfully.")
                
                logger.debug(
                    f"Retrieving Django Backend -------->  {request} created successfully.")
                logger.debug(
                    f"User {username} authenticated successfully.")
                return user_id
            else:
                logger.error(f"Failed to authenticate with external service: {status_code} {response_text}")
                return self.create_response({'detail': 'Invalid token.'}, status=401)
        except ClientConnectorError as e:
            logger.error(f"Connection error: {e}")
            return self.create_response({'detail': 'Connection error with authentication service.'}, status=500)
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error: {e}")
            return self.create_response({'detail': 'Timeout error with authentication service.'}, status=500)
        except Exception as e:
            logger.error(
                f"Error communicating with authentication service: {e}")
            return self.create_response({'detail': 'Error communicating with authentication service.'}, status=500)

    def authenticate_sync(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.warning("No Authorization header provided.")
            return self.create_response({'detail': 'Authorization header required.'}, status=401)

        auth_url = settings.EXTERNAL_AUTH_URL
        logger.info(f"Attempting to connect to auth service at {auth_url}")

        try:
            #auth_data, status_code, response_text =  fetch_auth_data(auth_url, {'Authorization': auth_header})
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            auth_data, status_code, response_text = loop.run_until_complete(
                fetch_auth_data(auth_url, {'Authorization': auth_header}))
            loop.close()
            logger.error(f"Retrieving the authData: {status_code}---->{auth_data}----> {response_text}")
            if status_code == 200 and auth_data:
                user_id = auth_data.get('user_id')
                username = auth_data.get('username')
                # Create a simple user object for request context, without saving to DB
            
                logger.debug(
                    f"Retrieving Django Backend -------->  {user} created successfully.")
                
                logger.debug(
                    f"User {username} authenticated successfully.")
                return user_id
            else:
                logger.error(f"Failed to authenticate with external service: {status_code} {response_text}")
                return self.create_response({'detail': 'Invalid token.'}, status=401)
        except ClientConnectorError as e:
            logger.error(f"Connection error: {e}")
            return self.create_response({'detail': 'Connection error with authentication service.'}, status=500)
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error: {e}")
            return self.create_response({'detail': 'Timeout error with authentication service.'}, status=500)
        except Exception as e:
            logger.error(
                f"Error communicating with authentication service: {e}")
            return self.create_response({'detail': 'Error communicating with authentication service.'}, status=500)
    def create_response(self, data, status):
        response = Response(data, status=status)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        return response
    
        # permission_classes = [IsAuthenticatedCustom] 
    def authenticate_and_dispatch(self,request, auth_response,*args, **kwargs):
        logger.debug("Async authenticate and dispatch method called in YourModelViewSet")
        if auth_response is not None:
            logger.debug(f"Authentication succeeded, auth_response ---> {auth_response}")    
            request.user = auth_response
            
        else:
            request.user = None
            request.is_active = False

        logger.debug(f"Authentication succeeded, proceeding to super().dispatch---> {request.user }")
        response = super().dispatch(request, *args, **kwargs)
        logger.debug(f"Authentication succeeded, async response---> {response}")
        return  response

    def dispatch(self, request, *args, **kwargs):
        logger.debug(f"Dispatch method called in ProductViewSet ---> {self.authenticate_async}")
        if asyncio.iscoroutinefunction(self.authenticate_async):
            logger.debug("Calling authenticate_async method")
            # Use async_to_sync to properly handle the async call
            auth_response = async_to_sync(self.authenticate_async)(request)
        else:
            auth_response = self.authenticate_sync(request)

        logger.debug(f"auth_response -----> {auth_response}")
        response = self.authenticate_and_dispatch(request, auth_response, *args, **kwargs)
        logger.debug(f"Dispatch method completed in ProductViewSet -----> {response}")
        return response
    
class ProcessUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Middleware logic before the view (and later middleware) are called
        logger.debug(f"ProcessUserMiddleware called with user: {request.user}")
        if request.user:
            logger.debug(f"User {request.user} is authenticated")

        response = self.get_response(request)

        # Middleware logic after the view is called
        return response