
from django.apps import AppConfig
from django.conf import settings




class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    
    def ready(self):
        from .utils import start_consumer_with_retries
        start_consumer_with_retries()
