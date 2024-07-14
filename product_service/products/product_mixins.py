from functools import wraps
import logging
from django.db import models
from django.utils import timezone
from .middlewares import SetLastModifiedBy
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)

class AuditLogMixin(models.Model):
    class Meta:
        abstract = True
   
    def save(self, *args, **kwargs):
        from .models import ProductAuditLog
        logger.info(f'Getting the productInfo here -----------------> {self}')
        user = kwargs.pop('last_modified_by', None)
        if self.pk:
            # Existing product, log changes
            old_instance = self.__class__.objects.get(pk=self.pk)
            for field in self._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name)
                new_value = getattr(self, field_name)
                if old_value != new_value:
                    ProductAuditLog.objects.create(
                        product=self,
                        action='UPDATE',
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        user=user,
                        timestamp=timezone.now()
                    )
            self.is_audited = False  # Reset audited status
        else:
            super().save(*args, **kwargs)  # Save the new instance to generate a primary key
            for field in self._meta.fields:
                field_name = field.name
                new_value = getattr(self, field_name)
                ProductAuditLog.objects.create(
                    product=self,
                    action='CREATE',
                    field_name=field_name,
                    old_value='',
                    new_value=new_value,
                    user=user,
                    timestamp=timezone.now()
                )
        self.last_modified = timezone.now()
        super().save(*args, **kwargs)
    def log_changes(self):
        logger.info(f"Product {self.id} - {self.name} changes logged.")