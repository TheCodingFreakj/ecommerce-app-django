from django.db import models
from django.contrib.postgres.fields import ArrayField

class Order(models.Model):
    customer_info = models.IntegerField()
    items = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    email = models.CharField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_info= models.CharField()
    billing_address= models.CharField()
    order_status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

       
