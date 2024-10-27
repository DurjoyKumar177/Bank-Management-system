from typing import Any
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from .constants import GENDER_TYPE,ACCOUNT_TYPE
from .models import UserBankAccount,UserAddress

class UserRegistrationForm(UserCreationForm):
    birth_date = forms.DateField(widget= forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length= 100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    class Meta:
        model = User
        fields = ['username', 'password1','password2','first_name','last_name','email','birth_date','account_type','gender','city','postal_code','street_address','country']
        
    def save(self, commit= True):
        our_user = super().save(commit=False) #ami database a data save korbo na akhon
        if commit== True:
            our_user.save() #user model e data save korlam
            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')
            birth_date = self.cleaned_data.get('birth_date')
            city = self.cleaned_data.get('city')
            street_address = self.cleaned_data.get('street_address')
            
            
            UserAddress.objects.create(
                user = our_user,
                postal_code = postal_code,
                country = country,
                city = city,
                street_address = street_address,
            )
            
            UserBankAccount.objects.create(
                user = our_user,
                account_type = street_address,
                gender = gender,
                birth_date = birth_date,
                account_no = 100000+ our_user.id #100000 er por userId plus hobe.
            )
            return our_user