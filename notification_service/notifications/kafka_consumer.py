from kafka import KafkaConsumer
from django.conf import settings
import ssl
import json

from .logsConsumer import log_api_error, log_transaction, log_unusual_activity
from .loggin_config import logger

class KafkaConsumerService:
    def __init__(self, topic):
        context = ssl.create_default_context()
        context.load_verify_locations(settings.KAFKA_CA_CERT)
        context.load_cert_chain(certfile=settings.KAFKA_CLIENT_CERT, keyfile=settings.KAFKA_CLIENT_KEY)

        self.consumer = KafkaConsumer(
            topic,
            enable_auto_commit=False,  # Disable auto commit
            bootstrap_servers=settings.KAFKA_BROKER_URLS,
            client_id = "LOGS_AGRREGATER",
            group_id = "LOGS_AGRREGATER_GROUP",
            # sasl_mechanism = 'SCRAM-SHA-256',
            # sasl_plain_username=settings.KAFKA_USERNAME,
            # sasl_plain_password=settings.KAFKA_PASSWORD,
            security_protocol = "SSL",
            ssl_context=context,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
# .poll().values()
    def consume_messages(self):
        print("Printing message using SSL---------------------------------------------------> ")
        while True:
           for message in self.consumer:
              print(f"Got message using SSL--------------------------------------------------->  {message.value}")
        # for message in self.consumer:
              logger.debug(f"Received Message------->: {message.value}")
              self.process_message(message.value)
              self.consumer.commit()


    def process_message(self, message):
        logger.debug(f"Received Message------->: {message}")
        try:
            message_type = message.get('type')
            if message_type == 'api_error_log':
                log_api_error(message)
            elif message_type == 'transaction':
                log_transaction(message)
            elif message_type == 'unusual_activity':
                log_unusual_activity(message)
            else:
                logger.debug(f"Unknown message type------->: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message------->: {e}")
                  
