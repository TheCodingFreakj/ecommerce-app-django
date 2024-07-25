# orders/services.py
import datetime
from .utils import send_to_kafka
from .kafka_producer import KafkaProducerPool
from .builders import OrderBuilder
from .loggin_config import logger


import datetime
from django.db import models
from .builders import OrderBuilder
from .loggin_config import logger

class OrderService:
    @staticmethod
    def create_order(user, total_amount):
        order_builder = OrderBuilder()
        logger.debug(f"OrderService In in-house order creation------> {order_builder.customer_info},{user}")
        
        order = (
            order_builder 
            .set_email("pallavidapriya75@gmail.com")      
            .set_customer_info(user)
            .set_items(["item1", "item2"])
            .set_total_amount(total_amount)
            .set_billing_address("123 Main St, Anytown, USA")
            .set_payment_info("Credit Card")
            .set_order_status("Processing")
            .set_created_at(datetime.datetime.now().isoformat())
            .set_updated_at(datetime.datetime.now().isoformat())
            .build()
        )
        
        logger.debug(f"OrderService In in-house order creation after calling the setups------> {order.customer_info}")
        return order

    @staticmethod
    def update_order_status(order, set_order_status):
        order.set_order_status = set_order_status
        order.asave()  # Use Django's asynchronous save method





import datetime
import httpx
from django.conf import settings
from .utils import send_to_kafka
from .kafka_producer import KafkaProducerPool
from .loggin_config import logger

class PaymentService:
    @staticmethod
    def initiate_payment(order, payment_type, customer_info, total_amount, transaction_id, ip_address):
        payload = {
            'order_id': order,
            'total_amount': total_amount,
            'user_id': customer_info,
            'payment_type': payment_type,
            'transaction_id': transaction_id,
            'ip_address': ip_address
        }
        logger.debug("Initializing KafkaProducerPool for payment initiation")
        producer_pool = KafkaProducerPool().initialize()  # Ensure singleton instance

        try:
            logger.debug(f"Calling the payment service handler here with amount {total_amount}")
            with httpx.Client() as client:
                response = client.post('https://payment-service-ap4j.onrender.com/api/payments/', json=payload, timeout=30.0)
                logger.debug(f"Payment service response received: {response}")

                response.raise_for_status()
                payment_data = response.json()
                logger.debug(f"Payment data parsed: {payment_data}")

                transaction_data = {
                    'transaction_id': transaction_id,
                    'user_id': customer_info,
                    'payment_method': "POST",
                    'status': 'processing',
                    'initiated_at': datetime.datetime.now().isoformat(),
                    'location': ip_address
                }
                send_to_kafka(producer_pool, transaction_data)
                return payment_data
        except httpx.HTTPStatusError as e:
            logger.error(f"Payment initiation failed for order {order}: {e}, Response content: {response.content}")
            transaction_data = {
                'transaction_id': transaction_id,
                'user_id': customer_info,
                'payment_method': "POST",
                'status': 'failed',
                'failed_reason': str(e),
                'initiated_at': datetime.datetime.now().isoformat(),
                'location': ip_address
            }
            send_to_kafka(producer_pool, transaction_data)
            return {"error": str(e), "status_code": response.status_code, "content": response.content.decode('utf-8')}
        except httpx.RequestError as e:
            logger.error(f"Payment initiation failed for order {order}: {e}")
            transaction_data = {
                'transaction_id': transaction_id,
                'user_id': customer_info,
                'payment_method': "POST",
                'status': 'failed',
                'failed_reason': str(e),
                'initiated_at': datetime.datetime.now().isoformat(),
                'location': ip_address
            }
            send_to_kafka(producer_pool, transaction_data)
            return {"error": str(e)}
