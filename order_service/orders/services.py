# orders/services.py
from .builders import OrderBuilder
import logging
import requests
class OrderService:
    @staticmethod
    def create_order(user, total_amount):
        order_builder = OrderBuilder()
        order = (order_builder
         .set_customer_info("John Doe")
         .set_email("pallavidapriya75@gmail.com")
         .set_items(["item1", "item2"])
         .set_total_amount("123 Main St, Anytown, USA")
         .set_billing_address("123 Main St, Anytown, USA")
         .set_payment_info("Credit Card")
         .set_order_status("Processing")
         .set_created_at({"created_at": "2024-07-20"})
         .set_updated_at("Please deliver between 9 AM and 5 PM")
         .build())
        return order

    @staticmethod
    def update_order_status(order, set_order_status):
        order.set_order_status = set_order_status
        order.save()






logger = logging.getLogger(__name__)

class PaymentService:
    @staticmethod
    def initiate_payment(order):
        try:
            # Call to external payment gateway API
            response = requests.post('https://payment_service:8004/payments', json={
                'order_id': order.id,
                'amount': order.total_amount,
                'user_id': order.user.id, 
                'payment_type': "razorpay"
            })
            response.raise_for_status()
            payment_data = response.json()
            return payment_data
        except requests.RequestException as e:
            logger.error(f"Payment initiation failed for order {order.id}: {e}")
            raise

