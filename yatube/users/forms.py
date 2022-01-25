from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, \
    PasswordChangeForm as PassChangeF

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PasswordChangeForm(PassChangeF):
    old_password = forms.CharField(
        label="Старый пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': True})
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(
            attrs={'autofocus': True}
        )
    )
    new_password2 = forms.CharField(
        label="Подтверждение нового пароля",
        widget=forms.PasswordInput(
            attrs={'autofocus': True}
        )
    )

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')
