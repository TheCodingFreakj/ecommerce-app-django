# orders/viewsets.py
import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from .services import OrderService, PaymentService

logger = logging.getLogger(__name__)
class OrderViewSet(viewsets.ViewSet):
    def create(self, request):
        user = 1
        total_amount = request.data.get('total_amount')
        try:
            # Step 1: Create Order
            order = OrderService.create_order(user, total_amount)
        except Exception as e:
            logger.error(f"Order creation failed for user {user}: {e}")
            return Response({'status': 'error', 'message': 'Order creation failed. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            # Step 2: Initiate Payment (only if order creation is successful)
            payment = PaymentService.initiate_payment(order)

            logger.error(f"Payment initiation {payment}")
        
        except Exception as e:
            logger.error(f"Payment initiation failed for order {order.id}: {e}")
            # OrderService.update_order_status(order, 'Failed')
            # NotificationService.send_payment_failed_notification(user, order)
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

