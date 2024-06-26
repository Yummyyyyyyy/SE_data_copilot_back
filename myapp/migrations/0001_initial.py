# Generated by Django 4.2.7 on 2024-06-11 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(blank=True, max_length=50, null=True)),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('category', models.CharField(blank=True, max_length=50, null=True)),
                ('order_time', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'order_info',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(blank=True, max_length=50, null=True)),
                ('order_status', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'db_table': 'order_status',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OrderTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(blank=True, max_length=50, null=True)),
                ('transaction_id', models.BigIntegerField(blank=True, null=True)),
                ('order_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('paid_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('discount_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('order_channel', models.CharField(blank=True, max_length=20, null=True)),
                ('payment_method', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'db_table': 'order_transaction',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='RecipientInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(blank=True, max_length=50, null=True)),
                ('recipient_name', models.CharField(blank=True, max_length=50, null=True)),
                ('recipient_address', models.CharField(blank=True, max_length=100, null=True)),
                ('recipient_phone', models.CharField(blank=True, max_length=20, null=True)),
            ],
            options={
                'db_table': 'recipient_info',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='QueryRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('database', models.CharField(max_length=255)),
                ('query', models.TextField()),
                ('results', models.JSONField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
