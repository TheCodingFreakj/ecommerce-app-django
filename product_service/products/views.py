# views.py
import asyncio
from functools import wraps
import logging

from rest_framework import viewsets,status

from .middleware import IsAuthenticatedCustom


from rest_framework.permissions import AllowAny
from .mixins import AuthMixin

from rest_framework.response import Response
from .middlewares import  SetLastModifiedBy
from .models import Product
from .serializers import ProductSerializer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)


def set_last_modified_by(func):
    @wraps(func)
    def wrapper(viewset_instance, request, *args, **kwargs):
        logger.info(f"Intercepting the request at the decorator----------------> {request}")
        decorator_instance =  SetLastModifiedBy(func)
        return  decorator_instance(viewset_instance, request, *args, **kwargs)
    return wrapper

from rest_framework.permissions import BasePermission

# AuthMixin
class ProductViewSet(AuthMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedCustom] 
  

        
    @set_last_modified_by
    def create(self, request, *args, **kwargs):
        logger.info(f"Intercepting the request at the view----------------> {self}")
        logger.info(f"Creating a new product with data: {request.data}")
        return super().create(request, *args, **kwargs)

        
    def list(self, request, *args, **kwargs):
        # <products.views.ProductViewSet object at 0x7f0eada545e0>
        logger.debug(f"Intercepting self-------------------> {self}")
        logger.debug(f"Intercepting request-------------------> {request}")
        logger.debug(f"Intercepting args-------------------> {args}")
        logger.debug(f"Intercepting kwargs-------------------> {kwargs}")

        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        # <products.views.ProductViewSet object at 0x7f0eada545e0>
        logger.debug(f"Intercepting self-------------------> {self}")
        #<rest_framework.request.Request: GET '/api/products/1/'>
        logger.debug(f"Intercepting request-------------------> {request}")
        logger.debug(f"Intercepting args-------------------> {args}")
        #Intercepting kwargs-------------------> {'pk': '1'}
        logger.debug(f"Intercepting kwargs-------------------> {kwargs}")

        return super().retrieve(request, *args, **kwargs)

    # @set_last_modified_by
    # def update(self, request, *args, **kwargs):
    #     # Custom update logic
    #     return super().update(request, *args, **kwargs)
    # @set_last_modified_by
    # def destroy(self, request, *args, **kwargs):
    #     # Custom delete logic
    #     return super().destroy(request, *args, **kwargs)



# add custom logic before and after the default behavior, you can do so
    # def list(self, request, *args, **kwargs):
    # # Custom logic before the default list method
    # logger.debug("Custom logic before")

    # response = super().list(request, *args, **kwargs)

    # # Custom logic after the default list method
    # logger.debug("Custom logic after")

    # return response

