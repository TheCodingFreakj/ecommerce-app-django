import asyncio
from django.conf import settings
from .loggin_config import logger
from kafka.errors import NoBrokersAvailable

def send_to_kafka(producer, message_data):
    max_retries = 3
    backoff_factor = 2
    attempt = 0

    while attempt < max_retries:
        try:
            producer.send_message(settings.KAFKA_TOPIC, {'type': 'transaction', 'data': message_data})
            return
        except NoBrokersAvailable as e:
            attempt += 1
            logger.error(f"Kafka broker not available on attempt {attempt}: {e}")
            if attempt < max_retries:
                sleep_time = backoff_factor ** attempt
                logger.info(f"Retrying Kafka message send in {sleep_time} seconds...")
                
            else:
                logger.error(f"All Kafka broker retry attempts failed. Falling back.")
                fallback_log(message_data)

def fallback_log(message_data):
    logger.error(f"Fallback log: {message_data}")
    # Additional logging to file or database can be added here if needed
