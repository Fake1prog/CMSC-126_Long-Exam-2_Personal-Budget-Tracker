from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['default_currency', 'date_format_preference']
        widgets = {
            'default_currency': forms.Select(choices=[
                ('USD', 'US Dollar (USD)'),
                ('EUR', 'Euro (EUR)'),
                ('GBP', 'British Pound (GBP)'),
                ('JPY', 'Japanese Yen (JPY)'),
                ('CAD', 'Canadian Dollar (CAD)'),
                ('AUD', 'Australian Dollar (AUD)'),
                ('PHP', 'Philippine Peso (PHP)'),
            ]),
            'date_format_preference': forms.Select(choices=[
                ('MM/DD/YYYY', 'MM/DD/YYYY'),
                ('DD/MM/YYYY', 'DD/MM/YYYY'),
                ('YYYY-MM-DD', 'YYYY-MM-DD'),
            ])
        }