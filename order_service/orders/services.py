# orders/services.py
from .builders import OrderBuilder
import logging
logger = logging.getLogger(__name__)
import requests
class OrderService:
    @staticmethod
    def create_order(user, total_amount):
        order_builder = OrderBuilder()
        logger.debug(f"OrderService In in-house order creation------> {order_builder.customer_info},{user}")
        order = (order_builder 
         .set_email("pallavidapriya75@gmail.com")      
         .set_customer_info(user)
         .set_items(["item1", "item2"])
         .set_total_amount(total_amount)
         .set_billing_address("123 Main St, Anytown, USA")
         .set_payment_info("Credit Card")
         .set_order_status("Processing")
         .set_created_at("2024-07-20")
         .set_updated_at("2024-07-20")
         .build())
        logger.debug(f"OrderService In in-house order creation after calling the setups------> {order.customer_info}")
        return order

    @staticmethod
    def update_order_status(order, set_order_status):
        order.set_order_status = set_order_status
        order.save()







# https://payment-service-ap4j.onrender.com/api/payments/
class PaymentService:
    @staticmethod
    def initiate_payment(order, payment_type, customer_info,total_amount):
        try:
            logger.debug(f"Calling the payment service handler here with amount {total_amount}")
            response = requests.post('https://payment-service-ap4j.onrender.com/api/payments/', json={
                'order_id': order,
                'total_amount': total_amount,
                'user_id': customer_info, 
                'payment_type': payment_type
            })
            response.raise_for_status()
            payment_data = response.json()
            logger.debug(f"Getting the payment data back from payment service-----> {payment_data}")
            return payment_data
        except requests.RequestException as e:
            logger.error(f"Payment initiation failed for order {order}: {e}")
            raise

