# views.py
from functools import wraps
import logging
import os
from pathlib import Path
import requests
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .middleware import AuthMiddleware
from .middlewares import  SetLastModifiedBy
from .models import Product
from .serializers import ProductSerializer
from django.views.decorators.http import require_http_methods
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


async def set_last_modified_by(func):
    @wraps(func)
    async def wrapper(viewset_instance, request, *args, **kwargs):
        logger.info(f"Intercepting the request at the decorator----------------> {request}")
        decorator_instance = await SetLastModifiedBy(func)
        return await decorator_instance(viewset_instance, request, *args, **kwargs)
    return wrapper


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes=[AuthMiddleware]
    # def dispatch(self, request, *args, **kwargs):
    #     # Apply custom middleware before handling the request
    #     middleware = CustomMiddleware()
    #     response = middleware.process_request(request)
    #     if response:
    #         return response

    #     try:
    #         # Log the request details
    #         print(f"Request method: {request.method}")
    #         print(f"Request path: {request.path}")
    #         print(f"Request headers: {request.headers}")

    #         # Modify request data (e.g., add a custom attribute)
    #         request.custom_attr = "Processed by CustomMiddleware"

    #         # Call the superclass dispatch method to handle the request
    #         response = super().dispatch(request, *args, **kwargs)

    #         # Log the response details
    #         print(f"Response status: {response.status_code}")
    #         print(f"Response headers: {response.headers}")

    #         # Modify the response before returning it
    #         response['X-Custom-Header'] = 'Processed by CustomMiddleware'
    #     except Exception as e:
    #         # Handle exceptions and return a custom error response
    #         print(f"Error occurred: {str(e)}")
    #         response = Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #     # Apply custom middleware after handling the response
    #     return middleware.process_response(request, response)
    # @set_last_modified_by
    async def create(self, request, *args, **kwargs):
        logger.info(f"Intercepting the request at the view----------------> {self}")
        # Custom create logic
        response =await super().create(request, *args, **kwargs)
        return response
    # @set_last_modified_by
    # def update(self, request, *args, **kwargs):
    #     # Custom update logic
    #     return super().update(request, *args, **kwargs)
    # @set_last_modified_by
    # def destroy(self, request, *args, **kwargs):
    #     # Custom delete logic
    #     return super().destroy(request, *args, **kwargs)

