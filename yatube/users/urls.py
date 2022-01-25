# yatube/users/urls
from django.contrib.auth.views import LogoutView, \
    PasswordResetView, PasswordChangeDoneView, \
    PasswordResetDoneView, PasswordResetConfirmView, LoginView, \
    PasswordResetCompleteView
from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    # Авторизация+
    path('login/',
         LoginView.as_view(template_name='users/login.html'),
         name='login'),

    # Выход+
    path('logout/',
         LogoutView.as_view(template_name='users/logged_out.html'),
         name='logout'),

    # Регистрация+
    path('signup/',
         views.SignUp.as_view(),
         name='signup'),

    # Смена пароля+
    path('password_change/',
         views.PasswordChangeView.as_view(
             template_name='users/password_change_form.html'),
         name='password_change'),

    # Сообщение об успешном изменении пароля+
    path('password_change/done/',
         PasswordChangeDoneView.as_view(
             template_name='users/password_change_done.html'),
         name='password_change_done'),

    # Восстановление пароля+
    path('password_reset/',
         PasswordResetView.as_view(
             template_name='users/password_reset_form.html'),
         name='password_reset_form'),

    # Сообщение об отправке ссылки для восстановления пароля+
    path('password_reset/done/',
         PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'),
         name='password_reset_done'),

    # Вход по ссылке для восстановления пароля+
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),

    # Сообщение об успешном восстановлении пароля+
    path('reset/done/',
         PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),
]
