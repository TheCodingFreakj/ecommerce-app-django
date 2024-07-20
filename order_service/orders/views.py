# orders/viewsets.py
import logging
import time
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Order
from .services import OrderService, PaymentService

logger = logging.getLogger(__name__)
class OrderViewSet(viewsets.ViewSet):
    def create(self, request):
        user = 1
        total_amount = request.data.get('total_amount')
        payment_type = request.data.get('payment_type')
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
            logger.debug(f"Order Created In in-house order creation------> {order}")
        except Exception as e:
            logger.error(f"Order creation failed for user {user}: {e}")
            return Response({'status': 'error', 'message': 'Order creation failed. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        max_retries = 3
        backoff_factor = 2
        attempt = 0
        while attempt < max_retries:
            try:
                payment = PaymentService.initiate_payment(order.id, payment_type, order.customer_info, order.total_amount)
                logger.debug(f"Payment Initiated In in-house order creation handler------> {payment}")
                return Response({'status': 'success', 'message': payment}, status=status.HTTP_200_OK)
            except Exception as e:
                attempt += 1
                logger.error(f"Payment initiation failed for order {order.id} on attempt {attempt}: {e}")
                if attempt < max_retries:
                    sleep_time = backoff_factor ** attempt
                    logger.info(f"Retrying payment initiation in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"All retry attempts failed for order {order.id}")
                    return Response({'status': 'error', 'message': 'Payment initiation failed. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        #call the payments api
        # Step 2: Initiate Payment
        #payment_response = PaymentService.initiate_payment(order)

        # Step 3: Handle Payment Response
        #update the order_stattus and and call notification api
        # if payment_response['status'] == 'success':
        #     OrderService.update_order_status(order, 'Paid')
        #     NotificationService.send_payment_successful_notification(user, order)
        #     return Response({'status': 'success', 'message': 'Payment successful and order created'}, status=status.HTTP_201_CREATED)
        # else:
        #     OrderService.update_order_status(order, 'Failed')
        #     NotificationService.send_payment_failed_notification(user, order)
        #     return Response({'status': 'failure', 'message': 'Payment failed. Please try again'}, status=status.HTTP_400_BAD_REQUEST)

