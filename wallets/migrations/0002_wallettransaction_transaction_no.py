# Generated by Django 5.1.1 on 2024-10-27 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallettransaction',
            name='transaction_no',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
    ]