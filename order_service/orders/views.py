import datetime
import time
import uuid
from django.conf import settings
import requests
from rest_framework import viewsets, status
from rest_framework.response import Response

from .profiling import profile_view
from .utils import send_to_kafka
from .kafka_producer import KafkaProducerPool
from .models import Order
from .services import OrderService, PaymentService
from .logsProducer import send_log, get_user_location
from .loggin_config import logger

class OrderViewSet(viewsets.ViewSet):
    @profile_view
    def create(self, request):
        user = 1  # This should be dynamically set based on the authenticated user
        total_amount = request.data.get('total_amount')
        payment_type = request.data.get('payment_type')
        ip_address = request.data.get('ip_address')
        transaction_id = str(uuid.uuid4())

        # Fetch user location synchronously
        location = get_user_location(ip_address)
        
        # Declare KafkaProducerService instance
        logger.debug("Initializing KafkaProducerPool for order creation")
        producer = KafkaProducerPool().initialize()
        
        try:
            # Step 1: Create Order
            logger.debug("Creating order")
            orderObj = OrderService.create_order(user, total_amount)
            logger.debug(f"OrderObj Created ------------------->{orderObj.customer_info}, {str(orderObj)}")
            order = Order.objects.create(
                customer_info=orderObj.customer_info, 
                items=orderObj.items,
                total_amount=orderObj.total_amount,
                email=orderObj.email,
                payment_info=orderObj.payment_info,
                billing_address=orderObj.billing_address,
                order_status=orderObj.order_status,
            )
            
            if order:                             
                transaction_data = {
                    'transaction_id': transaction_id,
                    'user_id': user,
                    'payment_method': "POST",
                    'status': 'initiated',
                    'initiated_at': datetime.datetime.now().isoformat(),
                    'location': location
                }
                logger.debug("Sending order creation message to Kafka")
                send_to_kafka(producer, transaction_data)
                logger.debug(f"Message sent to Kafka: {transaction_data}")
                
        except Exception as e:
            logger.error(f"Order creation failed for user {user}: {e}")
            return Response({'status': 'error', 'message': 'Order creation failed. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        max_retries = 3
        backoff_factor = 2
        attempt = 0
            
        while attempt < max_retries:
            try:
                logger.debug(f"Initiating payment for order {order.id}, attempt {attempt}")
                payment = PaymentService.initiate_payment(order.id, payment_type, order.customer_info, order.total_amount, transaction_id, location)
                logger.debug(f"Payment response received: {payment}")
                if 'error' in payment:
                    raise Exception(payment['error'])

                transaction_data['status'] = 'completed'
                logger.debug(f"Sending payment completion message to Kafka for order {order.id}")
                send_to_kafka(producer, transaction_data)
                logger.debug(f"Payment completion message sent to Kafka: {transaction_data}")
                return Response({'status': 'success', 'message': payment}, status=status.HTTP_200_OK)
        
            except Exception as e:
                logger.error(f"Payment initiation failed for order {order.id} on attempt {attempt}: {e}")
                transaction_data.update({
                    'status': 'failed',
                    'failed_reason': str(e),
                    'attempt_count': attempt
                })
                logger.debug(f"Sending payment failure message to Kafka for order {order.id}, attempt {attempt}")
                send_to_kafka(producer, transaction_data)
                logger.debug(f"Payment failure message sent to Kafka: {transaction_data}")

                if isinstance(e, requests.RequestException):
                    api_error_log = {
                        'transaction_id': transaction_id,
                        'error_message': str(e),
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                    logger.debug(f"Sending API error log to Kafka for transaction {transaction_id}")
                    send_to_kafka(producer, api_error_log)
                    logger.debug(f"API error log sent to Kafka: {api_error_log}")
                
                attempt += 1 
                if attempt == max_retries:
                    unusual_activity_log = {
                        'transaction_id': transaction_id,
                        'user_id': user,
                        'location': location,
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                    logger.debug(f"Sending unusual activity log to Kafka for transaction {transaction_id}")
                    send_to_kafka(producer, unusual_activity_log)
                    logger.debug(f"Unusual activity log sent to Kafka: {unusual_activity_log}")
                   
                if attempt < max_retries:
                    sleep_time = backoff_factor ** attempt
                    logger.debug(f"Retrying payment initiation in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"All retry attempts failed for order {order.id}")
                    send_to_kafka(producer, transaction_data)
                    return Response({'status': 'error', 'message': 'Payment initiation failed. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
