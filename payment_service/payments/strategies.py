# payments/strategies.py
import razorpay
import requests
import logging

from .models import Payment
from django.conf import settings
logger = logging.getLogger(__name__)
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def initiate_payment(self, order):
        pass
class StripePaymentStrategy(PaymentStrategy):
    def initiate_payment(self, order):
        try:
            response = requests.post('https://stripe.example.com/pay', json={
                'order_id': order.id,
                'amount': order.total_amount,
                'user_id': order.user.id
            })
            response.raise_for_status()
            payment_data = response.json()

            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                status=payment_data['status'],
                transaction_id=payment_data.get('transaction_id')
            )
            return payment
        except requests.RequestException as e:
            logger.error(f"Stripe payment initiation failed for order {order.id}: {e}")
            Payment.objects.create(
                order=order,
                amount=order.total_amount,
                status='failure'
            )
            raise

class PayPalPaymentStrategy(PaymentStrategy):
    def initiate_payment(self, order):
        try:
            response = requests.post('https://paypal.example.com/pay', json={
                'order_id': order.id,
                'amount': order.total_amount,
                'user_id': order.user.id
            })
            response.raise_for_status()
            payment_data = response.json()

            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                status=payment_data['status'],
                transaction_id=payment_data.get('transaction_id')
            )
            return payment
        except requests.RequestException as e:
            logger.error(f"PayPal payment initiation failed for order {order.id}: {e}")
            Payment.objects.create(
                order=order,
                amount=order.total_amount,
                status='failure'
            )
            raise


class RazorPayStrategy(PaymentStrategy):
    def initiate_payment(self, order):
        try:

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_order = client.order.create(
                {"amount": int(order.total_amount) * 100, "currency": "INR", "payment_capture": "1"}
            )
           
           
            razorpay_order.raise_for_status()
            payment_data = razorpay_order.json()

            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                status=payment_data['status'],
                transaction_id=razorpay_order.get('id')
            )
            return payment
        except requests.RequestException as e:
            logger.error(f"PayPal payment initiation failed for order {order.id}: {e}")
            Payment.objects.create(
                order=order,
                amount=order.total_amount,
                status='failure'
            )
            raise        