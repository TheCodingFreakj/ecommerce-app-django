import logging
from django.core.management.base import BaseCommand
from ...models import Product, CronJobStatus
from django.db import transaction

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

logger.info("process_product_changes command loaded")

class Command(BaseCommand):
    help = 'Process and audit product changes'

    def handle(self, *args, **kwargs):
        logger.info('Starting process_product_changes command.')
        
        job_status, created = CronJobStatus.objects.get_or_create(job_name='process_product_changes')
        if job_status.is_running:
            self.stdout.write('Job is already running.')
            logger.info('Job is already running. Exiting command.')
            return

        job_status.is_running = True
        job_status.save()
        
        try:
            self.process_products()
        except Exception as e:
            logger.error(f"Error processing products: {e}")
        finally:
            job_status.is_running = False
            job_status.save()
            logger.info('Finished process_product_changes command.')

    def process_products(self):
        logger.info('Processing products...')
        products = Product.objects.filter(status='unaudited-version-1', is_audited=False)[:10]
        for product in products:
            logger.info(f"Processing product: {product.id} - {product.name}")
            self.process_product(product)
        logger.info('Finished processing products.')

    @transaction.atomic
    def process_product(self, product):
        try:
            product.status = 'audited'
            product.is_audited = True
            product.save()
            product.log_changes()
            logger.info(f"Product {product.id} - {product.name} audited successfully.")
        except Exception as e:
            logger.error(f"Error processing product {product.id} - {product.name}: {e}")
            raise
