# your_app/management/commands/create_products.py
from django.core.management.base import BaseCommand
from ...models import Product
from random import randint, uniform
import faker

class Command(BaseCommand):
    help = 'Create 100 products in the database'

    def handle(self, *args, **kwargs):
        fake = faker.Faker()
        for _ in range(100):
            name = fake.unique.company()
            description = fake.text()
            price = round(uniform(10.0, 100.0), 2)
            status = 'unaudited-version-1'
            is_audited = False

            Product.objects.create(
                name=name,
                description=description,
                price=price,
                status=status,
                is_audited=is_audited
            )
        self.stdout.write(self.style.SUCCESS('Successfully created 100 products'))
