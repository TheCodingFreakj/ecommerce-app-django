# Generated by Django 5.0.7 on 2024-07-19 19:59

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_info', models.IntegerField()),
                ('items', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, size=None)),
                ('email', models.CharField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_info', models.CharField()),
                ('billing_address', models.CharField()),
                ('order_status', models.CharField(default='Pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]