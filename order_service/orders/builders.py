import logging
logger = logging.getLogger(__name__)

class Order:
    def __init__(self,email, customer_info,items, total_amount, billing_address,  payment_info, order_status, created_at, updated_at):
        logger.debug(f"Order Object set up before------> {customer_info}")
        logger.debug(f"Order Object set up before------> {items}")
        logger.debug(f"Order Object set up before------> {email}")
        self.email = email
        self.customer_info = customer_info
        self.items = items
        self.total_amount = total_amount
        self.billing_address = billing_address
        self.payment_info = payment_info
        self.order_status = order_status
        self.created_at = created_at
        self.updated_at = updated_at
        logger.debug(f"Order Object set up after------> {customer_info}")

   

class OrderBuilder:
    def __init__(self):
        self.email = None
        self.customer_info = None
        self.items = []
        self.total_amount = None
        self.billing_address = None
        self.payment_info = None
        self.order_status = None
        self.created_at = None
        self.updated_at = None


    def set_email(self, email):
        self.email = email
        return self

    def set_customer_info(self, customer_info):
        self.customer_info = customer_info
        return self

    def set_items(self, items):
        self.items = items
        return self

    def set_total_amount(self, total_amount):
        self.total_amount = total_amount
        return self

    def set_billing_address(self, billing_address):
        self.billing_address = billing_address
        return self

    def set_payment_info(self, payment_info):
        self.payment_info = payment_info
        return self

    def set_order_status(self, order_status):
        self.order_status = order_status
        return self

    def set_created_at(self, created_at):
        self.created_at = created_at
        return self

    def set_updated_at(self, updated_at):
        self.updated_at = updated_at
        return self
    

    def build(self):
        logger.debug(f"Order In build methd------> {self.email}")
        logger.debug(f"Order In build methd------> {self.customer_info}")
        logger.debug(f"Order In build methd------> {self.items}")
        return Order(
        self.email,
        self.customer_info,
        self.items,
        self.total_amount,
        self.billing_address,
        self.payment_info,
        self.order_status,
        self.created_at,
        self.updated_at,
        )
