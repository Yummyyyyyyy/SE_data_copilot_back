# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class QueryRecord(models.Model):
    database = models.CharField(max_length=255)
    query = models.TextField()
    results = models.JSONField()  # assuming Django 3.1+ for JSONField
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.database} - {self.query[:50]}"


class OrderInfo(models.Model):
    order_id = models.CharField(max_length=50, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    order_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_info'


class OrderStatus(models.Model):
    order_id = models.CharField(max_length=50, blank=True, null=True)
    order_status = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_status'


class OrderTransaction(models.Model):
    order_id = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.BigIntegerField(blank=True, null=True)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    order_channel = models.CharField(max_length=20, blank=True, null=True)
    payment_method = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_transaction'


class RecipientInfo(models.Model):
    order_id = models.CharField(max_length=50, blank=True, null=True)
    recipient_name = models.CharField(max_length=50, blank=True, null=True)
    recipient_address = models.CharField(max_length=100, blank=True, null=True)
    recipient_phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'recipient_info'
