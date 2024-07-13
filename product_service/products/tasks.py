# products/tasks.py
from celery import shared_task
from django.core.management import call_command
from .cron_manager import CronJobManager


@shared_task
def process_product_changes_task():
    cron_job_manager = CronJobManager()
    if not cron_job_manager.is_running():
        cron_job_manager.start()
    cron_job_manager.run()    
