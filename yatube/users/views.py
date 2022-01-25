# users/views.py
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm, PasswordChangeForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/signup.html'


class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('users:password_change_form')
    template_name = 'users/password_change_form.html'
