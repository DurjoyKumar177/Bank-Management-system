from django.contrib import messages
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from transactions.constants import DEPOSIT, WITHDRAWAL, LOAN, LOAN_PAID, TRANSFER
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404,redirect
from django.views import View
from datetime import datetime
from django.db.models import Sum
from transactions.forms import DepositForm, WinthdrawForm, LoanRequestForm, FundTransferForm
from transactions.models import Transaction
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

def send_transaction_email(user_account, amount, subject, template, receiver=None, sender=None):
    
    user = user_account.user
    message = render_to_string(template, {
        'user': user,
        'amount': amount,
        'receiver': receiver,
        'sender': sender
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()
class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                'account' : self.request.user.account,
                
            }
        )
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title' : self.title
        })
        
        return context
    
    
class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'
    
    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        account.save(
            update_fields=['balance']
        )
        
        messages.success(
            self.request,
            f'{"{:.2f}".format(float(amount))} $ was deposited to your account successfully')
        send_transaction_email(self.request.user, amount, 'Deposit Message','transactions/deposit_email.html')
        return super().form_valid(form)
    
    
class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WinthdrawForm
    title = 'Withdrawal'
    
    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        
        self.request.user.account.balance -= form.cleaned_data.get('amount')
        self.request.user.account.save(
            update_fields=['balance']
        ) 
        
        messages.success(
            self.request,
            f'Successfully withdrawn {"{:.2f}".format(float(amount))} $ from your account')
        send_transaction_email(self.request.user, amount, 'Withdrawal Message','transactions/withdraw_email.html')
        return super().form_valid(form)
    
    
class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Loan Request'
    
    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        
        current_loan_count = Transaction.objects.filter(
            account=self.request.user.account, transaction_type=LOAN,loan_approve=True).count()
        if current_loan_count >= 3:
            return HttpResponse(
                "You can't request for loan more than 3 times"
            )
        
        messages.success(
            self.request,
            f'Loan request for {"{:.2f}".format(float(amount))} $ submitted successfully')
        send_transaction_email(self.request.user, amount, 'Loan Request Message','transactions/loan_email.html')
        return super().form_valid(form)
    
    
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        ).order_by('-timestamp')  # Show newest transactions first

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account,
            'transactions': self.object_list  # Pass the transactions to the template context
        })

        return context
class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        if loan.loan_approve:
            user_account = loan.account
            
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                
                loan.loan_approve = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                messages.success(
                    self.request,
                    f'Loan amount for {"{:.2f}".format(float(loan.amount))} $ was paid successfully')
                send_transaction_email(self.request.user, loan.amount, 'Loan paid Message','transactions/loan_pay.html')
        
                return redirect('loan_list')
            else:
                messages.error(
                    self.request,
                    f'Loan amount is greater than your available balance'
                    )
        return redirect('loan_list')
    
class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans'
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account,transaction_type=3)
        print(queryset)
        return queryset
    
class TransferFundsView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = FundTransferForm
    template_name = 'transactions/fund_transfer.html'
    
    def get_initial(self):
        initial = {'transaction_type': TRANSFER}
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['account'] = self.request.user.account  # Pass the sender's account to the form
        return kwargs
    
    def form_valid(self, form):
        sender_account = self.request.user.account
        receiver_account = form.cleaned_data['receiver']
        amount = form.cleaned_data['amount']
        
        # Update balances for sender and receiver
        sender_account.balance -= amount
        receiver_account.balance += amount
        sender_account.save()
        receiver_account.save()
        
        transaction = form.save(commit=False)
        transaction.account = sender_account  
        transaction.receiver = receiver_account
        transaction.transaction_type = TRANSFER
        transaction.balance_after_transaction = sender_account.balance
        transaction.save() 
        
        messages.success(self.request, f'Successfully transferred ${amount} to {receiver_account.user.username} (Account No: {receiver_account.account_no}).')
        send_transaction_email(sender_account, amount, 'Fund Transfer Message','transactions/fund_transfer_sender_email.html', receiver_account, sender_account)
        send_transaction_email(receiver_account, amount, 'Fund Receive Message','transactions/fund_transfer_receiver_email.html',receiver_account, sender_account)

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('transaction_report') 