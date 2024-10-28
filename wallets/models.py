from django.db import models
from accounts.models import User
from orders.models import Order
from django.utils import timezone
import uuid

# Create your models here.
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.user.email
    

    def add_transaction(self, transaction_type, amount, description="", order=None):
        """Helper method to create Wallet Transaction history"""
        WalletTransaction.objects.create(
            wallet = self,
            transaction_type = transaction_type,
            amount = amount,
            description = description,
            order = order
        )
    

    def deposit(self, amount, description=""):
        """Add funds to the Wallet"""
        if amount > 0:
            self.balance += amount
            self.save()
            self.add_transaction('DEPOSIT', amount=amount, description=description)
            return True

    def withdraw(self, amount, description="", order=None):
        """Withdraw funds from the wallet if sufficient funds exist"""
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            self.save()
            self.add_tranasaction('WITHDRAW', amount=amount, description=description, order=order)
            return True
    

    def refund(self, amount, order, description=''):
        """Add a refund amount to the wallet"""
        if amount > 0:
            self.balance += amount
            self.save()

            # create a transaction record for the refund
            self.add_transaction('REFUND', amount=amount, description=description, order=order)



class WalletTransaction(models.Model):
    TRANSACTION_CHOICES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAW', 'Withdraw'),
        ('REFUND', 'Refund'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name="transactions")
    transaction_no = models.CharField(max_length=30, unique=True, blank=True, null=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True, related_name="refund_transaction")
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']

    
    def save(self, *args, **kwargs):
        if not self.transaction_no:
            unique_id = uuid.uuid4().hex[:6].upper()
            timestamp = timezone.now().strftime("%y%m%d%H%M%S")
            self.transaction_no = f"FSRV-{timestamp}-{unique_id}"
        super().save(*args, **kwargs)

