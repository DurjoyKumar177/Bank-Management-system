from django.contrib import admin
from .models import Transaction
from .views import send_transaction_email

# Register your models here.

@admin.register(Transaction)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'balance_after_transaction', 'transaction_type', 'loan_approve']
    
    def save_model(self, request, obj, form, change):

        obj.account.balance += obj.amount
        obj.balance_after_transaction = obj.account.balance
        obj.account.save()
        send_transaction_email(obj.account.user, obj.amount, 'Loan Approval Message','transactions/loan_approval.html')
        super().save_model(request, obj, form, change)
