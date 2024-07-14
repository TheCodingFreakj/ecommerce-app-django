# products/apps.py
import logging
from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    
    def ready(self):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("YourAppConfig is ready.")
        

