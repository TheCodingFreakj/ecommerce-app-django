# orders/services.py
import datetime
from .builders import OrderBuilder
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .logsProducer import send_log
from .loggin_config import logger
from rest_framework.response import Response
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







class PaymentService:
    session = None
    
    @staticmethod
    def get_session():
        if PaymentService.session is None:
            session = requests.Session()
            retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
            adapter = HTTPAdapter(max_retries=retries)
            session.mount('https://', adapter)
            PaymentService.session = session
        return PaymentService.session
    @staticmethod
    def initiate_payment(order, payment_type, customer_info,total_amount,transaction_id,ip_address):
        session = PaymentService.get_session()
        try:
            logger.debug(f"Calling the payment service handler here with amount {total_amount}")
            response = session.post('https://payment-service-ap4j.onrender.com/api/payments/', json={
                'order_id': order,
                'total_amount': total_amount,
                'user_id': customer_info, 
                'payment_type': payment_type,
                'transaction_id':transaction_id,
                'ip_address':ip_address
            })
            logger.debug(f"Getting the payment data back from payment service-----> {response}")
            response.raise_for_status()
            payment_data = response.json()
            logger.debug(f"Getting the payment data back from payment service after converting to json-----> {payment_data}")
            transaction_data = {
                    'transaction_id':transaction_id,
                    'user_id': customer_info,
                    'payment_method': "POST",
                    'status': 'processing',
                    'initiated_at': datetime.datetime.now().isoformat(),
                    'location': ip_address
            }
                # Log the transaction initiation
            send_log({'type': 'transaction', 'data': transaction_data})
            
           
            return  payment_data
        except requests.HTTPError as e:
            logger.error(f"Payment initiation failed for order {order}: {e}, Response content: {response.content}")
            transaction_data = {
                    'transaction_id':transaction_id,
                    'user_id': customer_info,
                    'payment_method': "POST",
                    'status': 'failed',
                    'failed_reason': str(e),
                    'initiated_at': datetime.datetime.now().isoformat(),
                    'location': ip_address
            }
                # Log the transaction initiation
            send_log({'type': 'transaction', 'data': transaction_data})
            return {"error": str(e), "status_code": response.status_code, "content": response.content.decode('utf-8')}
        except requests.RequestException as e:
            logger.error(f"Payment initiation failed for order {order}: {e}")
            transaction_data = {
                    'transaction_id':transaction_id,
                    'user_id': customer_info,
                    'payment_method': "POST",
                    'status': 'failed',
                    'failed_reason': str(e),
                    'initiated_at': datetime.datetime.now().isoformat(),
                    'location': ip_address
            }
                # Log the transaction initiation
            send_log({'type': 'transaction', 'data': transaction_data})
            return {"error": str(e)}