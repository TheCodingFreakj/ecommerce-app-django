# orders/viewsets.py
import datetime
import logging
import time
import uuid
import requests
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Order
from .services import OrderService, PaymentService
from .logsProducer import send_log, get_user_location
from .loggin_config import logger
class OrderViewSet(viewsets.ViewSet):
    def create(self, request):
        user = 1
        total_amount = request.data.get('total_amount')
        payment_type = request.data.get('payment_type')
        ip_address = request.data.get('ip_address')
        transaction_id = str(uuid.uuid4())
        location = get_user_location(ip_address)
        try:
            # Step 1: Create Order
            orderObj = OrderService.create_order(user, total_amount)
            logger.debug(f"OrderObj Created In in-house order creation------> {repr(orderObj)}")
            order = Order.objects.create(customer_info=orderObj.customer_info, 
                                         items=orderObj.items,
                                         total_amount=orderObj.total_amount,
                                         email=orderObj.email,
                                         payment_info=orderObj.payment_info,
                                         billing_address=orderObj.billing_address,
                                         order_status=orderObj.order_status,
                                         )
            transaction_data = {
                    'transaction_id':transaction_id,
                    'user_id': user,
                    'payment_method': "POST",
                    'status': 'initiated',
                    'initiated_at': datetime.datetime.now().isoformat(),
                    'location': location
            }
                # Log the transaction initiation
            send_log({'type': 'transaction', 'data': transaction_data})
            logger.debug(f"Order Created In in-house order creation------> {order}")
        except Exception as e:
            logger.error(f"Order creation failed for user {user}: {e}")
            return Response({'status': 'error', 'message': 'Order creation failed. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        max_retries = 3
        backoff_factor = 2
        attempt = 0
            
        while attempt < max_retries:
            try:

                payment = PaymentService.initiate_payment(order.id, payment_type, order.customer_info, order.total_amount, transaction_id,location)
                logger.debug(f"Payment Initiated In in-house order creation handler------> {payment}")
                if 'error' in payment:
                    raise Exception(payment['error'])
                transaction_data = {
                    'transaction_id':transaction_id,
                    'user_id': user,
                    'payment_method': "POST",
                    'status': 'completed',
                    'initiated_at': datetime.datetime.now().isoformat(),
                    'location': location
                }
                # Log the transaction initiation
                send_log({'type': 'transaction', 'data': transaction_data})
                return Response({'status': 'success', 'message': payment}, status=status.HTTP_200_OK)
        
            except Exception as e:
                attempt += 1
                transaction_data = {
                    'transaction_id':transaction_id,
                    'user_id': user,
                    'initiated_at': datetime.datetime.now().isoformat(),
                    'payment_method': "POST",
                    'status': 'failed',
                    'failed_reason':str(e),
                    'location': location,
                    'attempt_count':attempt
                }
                # Log the transaction initiation
                send_log({'type': 'transaction', 'data': transaction_data})

                # Check if the error is an API error
                if isinstance(e, requests.exceptions.RequestException):
                    # Log the API error
                    api_error_log = {
                        'transaction_id':transaction_id,
                        'error_message': str(e),
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                    send_log({'type': 'api_error', 'data': api_error_log})
                logger.error(f"Payment initiation failed for order {order.id} on attempt {attempt}: {e}")
                if attempt == 3:
                    unsual_activity_log = {
                        'transaction_id':transaction_id,
                        'user_id': user,
                        'location': location,
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                    send_log({'type': 'unusual_activity', 'data': unsual_activity_log})
                if attempt < max_retries:
                    sleep_time = backoff_factor ** attempt
                    logger.info(f"Retrying payment initiation in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"All retry attempts failed for order {order.id}")
                    return Response({'status': 'error', 'message': 'Payment initiation failed. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        

