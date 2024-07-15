import logging
from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class IsAuthenticatedCustom(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        logger.info(f"Hitting the customermiddle now---------------{request.user}")
        return True if request.user else False 