from django import forms
from .models import Transaction
from accounts.models import UserBankAccount

#we use the same form for multiple work
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount','transaction_type']
        
    def __init__(self,*args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True #ai field disable thakbe 
        self.fields['transaction_type'].widget = forms.HiddenInput() #user the hide kora thakbe
        
    def save(self, commit = True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()
    
class DepositForm(TransactionForm):
    def clean_amount(self):
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount')
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )
            
        return amount
    
class WinthdrawForm(TransactionForm):
    
    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )
            
        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )
            
        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                f'You can not withdrow more than your account balance '
            )
        return amount
    
class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        return amount
    
class FundTransferForm(forms.ModelForm):
    receiver_account_no = forms.CharField(max_length=12, label="Receiver's Account Number")  # Changed to match 'account_no'
    password = forms.CharField(widget=forms.PasswordInput, label="Your Password")
    
    class Meta:
        model = Transaction
        fields = ['amount', 'receiver_account_no', 'password']
        
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)  # Get sender's account from kwargs
        super().__init__(*args, **kwargs)
        
        # Set the sender's account on the instance for access in clean()
        if self.account:
            self.instance.account = self.account
    
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")
        receiver_account_no = cleaned_data.get("receiver_account_no")  # Updated to 'receiver_account_no'
        password = cleaned_data.get("password")
        sender = self.instance.account

        # Validate the receiver account number
        try:
            receiver = UserBankAccount.objects.get(account_no=receiver_account_no)  # Updated to 'account_no'
        except UserBankAccount.DoesNotExist:
            raise forms.ValidationError("Invalid receiver account number.")

        # Store the receiver for use in the view
        self.cleaned_data['receiver'] = receiver

        # Check sender's password
        if not sender.user.check_password(password):
            raise forms.ValidationError("Incorrect password.")

        # Ensure sender has enough balance
        if amount > sender.balance:
            raise forms.ValidationError("Insufficient balance.")
        
        return cleaned_data


