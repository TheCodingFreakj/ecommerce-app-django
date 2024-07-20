# orders/viewsets.py
import logging
from rest_framework import viewsets, status
from rest_framework.response import Response



logger = logging.getLogger(__name__)
class NotificationsViewSet(viewsets.ViewSet):
    def create(self, request):
       return NotImplemented()
