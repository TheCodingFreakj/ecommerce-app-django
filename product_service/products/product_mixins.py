# mixins.py

import logging
from django.utils import timezone
from django.db import models

logger = logging.getLogger(__name__)

class AuditLogMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from .models import ProductAuditLog
        logger.info(f'Getting the product info here -----------------> {self}')
        user = kwargs.pop('last_modified_by', None)
        is_create = not bool(self.pk)

        if not is_create:
            # Existing product, log changes
            old_instance = self.__class__.objects.get(pk=self.pk)
            changes = []
            for field in self._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name)
                new_value = getattr(self, field_name)
                if old_value != new_value:
                    logger.info(f'Field {field_name} changed from {old_value} to {new_value}')
                    changes.append(ProductAuditLog(
                        product=self,
                        action='UPDATE',
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        user=user,
                        timestamp=timezone.now()
                    ))
            if changes:
                ProductAuditLog.objects.bulk_create(changes)
        super().save(*args, **kwargs)

        if is_create:
            # New product, log creation
            logs = []
            for field in self._meta.fields:
                field_name = field.name
                new_value = getattr(self, field_name)
                logger.info(f'Creating audit log for field {field_name} with value {new_value}')
                logs.append(ProductAuditLog(
                    product=self,
                    action='CREATE',
                    field_name=field_name,
                    old_value='',
                    new_value=new_value,
                    user=user,
                    timestamp=timezone.now()
                ))
            ProductAuditLog.objects.bulk_create(logs)

        self.last_modified = timezone.now()
        logger.info(f"Product {self.id} - {self.name} changes logged.")
