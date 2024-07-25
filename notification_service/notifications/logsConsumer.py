# consumers.py

import pika
import json
from threading import Thread
from django.conf import settings
from .models import Transaction, UnusualActivity, APIErrorLog
from django.utils import timezone
from .loggin_config import logger

def log_transaction(data):
    logger.debug(f"Data coming for transaction--------------------->: {data}")
    try:

        transaction = Transaction.objects.create(
    user_id=data["data"].get("user_id"),
    transaction_id=data["data"].get("transaction_id"),
    payment_method=data["data"].get("payment_method"),
    status=data["data"].get("status"),
    initiated_at=data["data"].get("initiated_at") or None,
    completed_at=data["data"].get("completed_at") or None,
    failed_reason=data["data"].get("failed_reason") or None,
    api_error=data["data"].get("api_error") or None,
    location=data["data"].get("location") or None,
    attempt_count=data["data"].get("attempt_count", 0)  # Default to 0 if not present
)
        logger.debug(f"Transaction logged successfully: {transaction}")
    except Exception as e:
        logger.error(f"Error logging transaction: {e}")

def log_unusual_activity(data):
    logger.debug(f"Data coming for log_unusual_activity--------------------->: {data}")
    try:
        unusual_activity = UnusualActivity.objects.create(
            transaction_id=data["data"]["transaction_id"],
            user_id=data["data"]["user_id"],
            location=data["data"]["location"],
            timestamp=data["data"]["timestamp"]
        )
        logger.debug(f"Unusual activity logged successfully: {unusual_activity}")
    except Exception as e:
        logger.error(f"Error logging unusual activity: {e}")

def log_api_error(data):
    logger.debug(f"Data coming for log_api_error--------------------->: {data}")
    try:
        api_error_log = APIErrorLog.objects.create(
            transaction_id=data["data"]["transaction_id"],
            error_message=data["data"]["error_message"],
            timestamp=data["data"]["timestamp"]
        )
        logger.debug(f"API error logged successfully: {api_error_log}")
    except Exception as e:
        logger.error(f"Error logging API error: {e}")

def process_message(ch, method, properties, body):
    try:
        log_data = json.loads(body)
        if log_data['type'] == 'transaction':
            log_transaction(log_data['data'])
        elif log_data['type'] == 'unusual_activity':
            log_unusual_activity(log_data['data'])
        elif log_data['type'] == 'api_error':
            log_api_error(log_data['data'])
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def start_consumer():
    try:
        url = 'amqps://qszdxpbw:7H0HtHw6-gPkGC8KoIW-wHqUwTlaVzbp@cow.rmq2.cloudamqp.com/qszdxpbw'
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='logs')
        channel.basic_consume(queue='logs', on_message_callback=process_message, auto_ack=True)
        logger.debug("Starting RabbitMQ consumer")
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"AMQP Connection error: {e}")
    except pika.exceptions.ChannelClosedByBroker as e:
        logger.error(f"Channel closed by broker: {e}")
    except pika.exceptions.StreamLostError as e:
        logger.error(f"Stream lost error: {e}")
    except pika.exceptions.ProbableAuthenticationError as e:
        logger.error(f"Authentication error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
            logger.debug("Closed RabbitMQ connection")

def run_consumer():
    consumer_thread = Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()


