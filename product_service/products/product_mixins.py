from django.db import models
from django.utils import timezone



class AuditLogMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        from .models import ProductAuditLog
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
                    timestamp=timezone.now()
                )
        self.last_modified = timezone.now()
        super().save(*args, **kwargs)
