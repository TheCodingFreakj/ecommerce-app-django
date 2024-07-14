import logging
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model
from rest_framework.response import Response
import asyncio
from aiohttp import ClientSession, ClientConnectorError, ClientTimeout

logger = logging.getLogger(__name__)
UserModel = get_user_model()

async def fetch_auth_data(auth_url, headers):
    async with ClientSession(timeout=ClientTimeout(total=10)) as session:
        try:
            async with session.get(auth_url, headers=headers) as response:
                if response.status == 200:
                    return await response.json(), response.status, None
                else:
                    return None, response.status, await response.text()
        except ClientConnectorError as e:
            return None, None, str(e)
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error: {e}")
            return None, None, "Timeout error"

class AuthMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if asyncio.iscoroutinefunction(self.get_response):
            return self.async_call(request)
        return self.sync_call(request)

    async def async_call(self, request):
        # self.sanitize_host(request)
        response = await self.process_request_async(request)
        if response:
            return response

        response = await self.get_response(request)
        if asyncio.iscoroutine(response):
            response = await response

        response = await self.process_response_async(request, response)
        if asyncio.iscoroutine(response):
            response = await response
        return response

    def sync_call(self, request):
        # self.sanitize_host(request)
        response = self.process_request_sync(request)
        if response:
            return response

        response = self.get_response(request)
        if asyncio.iscoroutine(response):
            response = asyncio.run(response)

        response = self.process_response_sync(request, response)
        if asyncio.iscoroutine(response):
            response = asyncio.run(response)
        return response

    # def sanitize_host(self, request):
    #     # Sanitize HTTP_HOST header to remove the port number
    #     if 'HTTP_HOST' in request.META:
    #         host = request.META['HTTP_HOST']
    #         if ':' in host:
    #             request.META['HTTP_HOST'] = host.split(':')[0]

    async def process_request_async(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.warning("No Authorization header provided.")
            return Response({'detail': 'Authorization header required.'}, status=401)

        auth_url = settings.EXTERNAL_AUTH_URL
        logger.info(f"Attempting to connect to auth service at {auth_url}")

        try:
            auth_data, status_code, response_text = await fetch_auth_data(auth_url, {'Authorization': auth_header})
            if status_code == 200 and auth_data:
                user_id = auth_data.get('user_id')
                username = auth_data.get('username')

                user, created = await asyncio.to_thread(UserModel.objects.get_or_create, id=user_id, defaults={'username': username})
                if not created:
                    user.username = username
                    await asyncio.to_thread(user.save)

                request.user = user
                logger.info(f"User {user.username} authenticated successfully.")
            else:
                logger.error(f"Failed to authenticate with external service: {status_code} {response_text}")
                return Response({'detail': 'Invalid token.'}, status=401)
        except ClientConnectorError as e:
            logger.error(f"Connection error: {e}")
            return Response({'detail': 'Connection error with authentication service.'}, status=500)
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error: {e}")
            return Response({'detail': 'Timeout error with authentication service.'}, status=500)
        except Exception as e:
            logger.error(f"Error communicating with authentication service: {e}")
            return Response({'detail': 'Error communicating with authentication service.'}, status=500)

    def process_request_sync(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.warning("No Authorization header provided.")
            return Response({'detail': 'Authorization header required.'}, status=401)

        auth_url = settings.EXTERNAL_AUTH_URL
        logger.info(f"Attempting to connect to auth service at {auth_url}")

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            auth_data, status_code, response_text = loop.run_until_complete(fetch_auth_data(auth_url, {'Authorization': auth_header}))
            loop.close()
            if status_code == 200 and auth_data:
                user_id = auth_data.get('user_id')
                username = auth_data.get('username')

                user, created = UserModel.objects.get_or_create(id=user_id, defaults={'username': username})
                if not created:
                    user.username = username
                    user.save()

                request.user = user
                logger.info(f"User {user.username} authenticated successfully.")
            else:
                logger.error(f"Failed to authenticate with external service: {status_code} {response_text}")
                return Response({'detail': 'Invalid token.'}, status=401)
        except ClientConnectorError as e:
            logger.error(f"Connection error: {e}")
            return Response({'detail': 'Connection error with authentication service.'}, status=500)
        except asyncio.TimeoutError as e:
            logger.error(f"Timeout error: {e}")
            return Response({'detail': 'Timeout error with authentication service.'}, status=500)
        except Exception as e:
            logger.error(f"Error communicating with authentication service: {e}")
            return Response({'detail': 'Error communicating with authentication service.'}, status=500)

    async def process_response_async(self, request, response):
        return response

    def process_response_sync(self, request, response):
        return response
