# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        # Custom create logic
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Custom update logic
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Custom delete logic
        return super().destroy(request, *args, **kwargs)

