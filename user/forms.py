
from django import forms

from .models import User


class RegistrationForm(forms.ModelForm):
  password = forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder': 'Your password',
    'class': 'form-control',
  }))
  confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder': 'Confirm your password',
    'class': 'form-control',
  }))
  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'email', 'phone', 'password']

  def clean(self):
    cleaned_data = super(RegistrationForm, self).clean()
    password = cleaned_data.get('password')
    confirm_password = cleaned_data.get('confirm_password')

    if confirm_password != password:
      raise forms.ValidationError("Password does not match!")

  def __init__(self, *args, **kargs):
    super(RegistrationForm, self).__init__(*args, **kargs)
    self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name'
    self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name'
    self.fields['email'].widget.attrs['placeholder'] = 'Enter your email'
    self.fields['phone'].widget.attrs['placeholder'] = 'Enter your phone'

    for field in self.fields:
      self.fields[field].widget.attrs['class'] = 'form-control'
