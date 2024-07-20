from django.db import models
from django.utils import timezone

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    transaction_id = models.CharField()
    user_id = models.IntegerField()
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    initiated_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_reason = models.TextField(null=True, blank=True)
    api_error = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    attempt_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'logging_schema"."transaction'
    
class UnusualActivity(models.Model):
    transaction_id = models.CharField()
    user_id = models.IntegerField()
    location = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    class Meta:
        db_table = 'logging_schema"."unusual_activity'
    
class APIErrorLog(models.Model):
    transaction_id = models.CharField()
    error_message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'logging_schema"."api_error_log'   
