# products/cron_manager.py
import os
import django
import threading
import time

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_service.settings')

# Setup Django to work with the ORM
django.setup()

from django.core.management import call_command

class CronJobManager:
    _instance = None  # Class-level variable to hold the singleton instance
    _lock = threading.Lock()  # A lock to ensure thread safety

    def __new__(cls, *args, **kwargs):
        # Ensure that only one instance of the class is created
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CronJobManager, cls).__new__(cls, *args, **kwargs)
                cls._instance._initialized = False  # Flag to check if instance is initialized
            return cls._instance

    def __init__(self):
        # Initialize the instance only once
        if self._initialized:
            return
        self.job_thread = None  # Thread variable to run the cron job
        self._stop_event = threading.Event()  # Event to signal thread to stop
        self._initialized = True  # Mark the instance as initialized

    def start(self):
        # Start the cron job thread if it's not already running
        if self.job_thread and self.job_thread.is_alive():
            print("Cron job is already running.")
            return

        self._stop_event.clear()  # Clear the stop event
        self.job_thread = threading.Thread(target=self.run)  # Create a new thread
        self.job_thread.start()  # Start the thread
        print("Cron job started.")

    def stop(self):
        # Stop the cron job thread if it's running
        if self.job_thread and self.job_thread.is_alive():
            self._stop_event.set()  # Set the stop event
            self.job_thread.join()  # Wait for the thread to finish
            print("Cron job stopped.")

    def run(self):
        # Method that runs the actual cron job
        while not self._stop_event.is_set():
            try:
                call_command('process_product_changes')  # Run the management command
            except Exception as e:
                print(f"Error running command: {e}")
            time.sleep(3600)  # Wait for 1 hour before running again

    def is_running(self):
        # Check if the cron job thread is running
        return self.job_thread and self.job_thread.is_alive()
