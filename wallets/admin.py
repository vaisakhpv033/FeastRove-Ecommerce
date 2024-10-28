from django.contrib import admin
from .models import Wallet, WalletTransaction
# Register your models here.


class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at')

class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'order')


admin.site.register(Wallet, WalletAdmin)
admin.site.register(WalletTransaction, WalletTransactionAdmin)