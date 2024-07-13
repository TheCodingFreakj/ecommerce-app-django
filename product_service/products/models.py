from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .product_mixins import AuditLogMixin

class Product(AuditLogMixin, models.Model):
    STATUS_CHOICES = [
        ('unaudited-version-1', 'Unaudited Version 1'),
        ('audited', 'Audited'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='unaudited-version-1')
    last_modified = models.DateTimeField(auto_now=True)
    is_audited = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    

class ProductAuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.IntegerField()
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    field_name = models.CharField(max_length=50)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} - {self.action} - {self.field_name}"

class CronJobStatus(models.Model):
    job_name = models.CharField(max_length=255, unique=True)
    last_run = models.DateTimeField(auto_now=True)
    is_running = models.BooleanField(default=False)