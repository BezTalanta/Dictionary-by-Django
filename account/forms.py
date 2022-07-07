from django import forms
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    model = User
    username = forms.CharField
