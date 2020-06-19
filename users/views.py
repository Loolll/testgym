from django.shortcuts import render
from .forms import UserCreationForm, UserAuthForm, UserRestoreForm, UserEditForm, UserUpToAdminForm
from .models import CustomUser
from django.http import HttpResponseRedirect as HRR
from django.contrib.auth import login, logout, authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings
import random


def captcha_check():  # TODO on deploy
    return True


def user_creation_form_valid(data):
    if data['password1'] != data['password2']:
        return 'Введенные вами пароли не совпадают'
    if not all([x in "+0123456789" for x in data['phone']]):
        return 'Введите правильный номер телефона'
    if not all([x.lower() in 'abcdefghijklmnopqrstuvwyxzабвгдеёжзийклмнопрстуфхцчшщъыьэюя' for x in data['name']]):
        return 'Имя введено некорректно'
    if not all([x.lower() in 'abcdefghijklmnopqrstuvwyxzабвгдеёжзийклмнопрстуфхцчшщъыьэюя' for x in data['soname']]):
        return 'Фамилия введена некорректно'
    if len(CustomUser.objects.filter(email=data['email'])):
        return 'Аккаунт на данный email уже зарегистрирован'
    return True


def user_edit_form_valid(data):
    if not all([x in "+0123456789" for x in data['phone']]):
        return 'Введите правильный номер телефона'
    if not all([x.lower() in 'abcdefghijklmnopqrstuvwyxzабвгдеёжзийклмнопрстуфхцчшщъыьэюя' for x in data['name']]):
        return 'Имя введено некорректно'
    if not all([x.lower() in 'abcdefghijklmnopqrstuvwyxzабвгдеёжзийклмнопрстуфхцчшщъыьэюя' for x in data['soname']]):
        return 'Фамилия введена некорректно'
    return True


def registration(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'reg_form': UserCreationForm})
    elif request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            if captcha_check():  # TODO on deploy
                status = user_creation_form_valid(form.cleaned_data)
                if type(status) is bool:
                    CustomUser.objects.create_user(email=form.cleaned_data['email'],
                                                   password=form.cleaned_data['password1'],
                                                   phone=form.cleaned_data['phone'],
                                                   name=form.cleaned_data['name'],
                                                   soname=form.cleaned_data['soname'],
                                                   entity=form.cleaned_data['entity'])
                    return HRR('/users/auth/')
                else:
                    return render(request, 'signup.html', {'reg_form': form, 'header': status})
            else:
                return render(request, 'signup.html', {'reg_form': form, 'header': 'Капча неверна, попробуйте еще раз'})
        else:
            return render(request, 'signup.html', {
                'reg_form': form, 'header': 'Проверьте введенную вами информацию и попробуйте еще раз'})


def authorization(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'auth_form': UserAuthForm})
    elif request.method == 'POST':
        form = UserAuthForm(request.POST)
        if form.is_valid():
            user = authenticate(request, email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return HRR('/')
            else:
                return render(request, 'signin.html', {
                    'auth_form': form, 'header':
                    'Введенный вами email или пароль неверны'})
        else:
            return render(request, 'signin.html', {
                'auth_form': form, 'header':
                'Проверьте введенные вами данные и попробуйте еще раз'})


def restore(request):
    if request.method == 'GET':
        return render(request, 'restore.html', {'rest_form': UserRestoreForm})
    elif request.method == 'POST':
        form = UserRestoreForm(request.POST)
        if form.is_valid():
            if captcha_check():  # TODO on deploy
                try:
                    user = CustomUser.objects.get(email=form.cleaned_data['email'])
                except ObjectDoesNotExist:
                    user = None
                if user is not None:
                    new_pass = ''.join(['ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
                                        [random.randint(0, 61)] for _ in range(8)])
                    user.set_password(new_pass)
                    user.save()
                    send_mail(f'Ваш новый пароль на сайте {settings.SITE_NAME} !',
                              f'Ваш новый пароль:{new_pass}\n'
                              f'Ссылка на авторизацию: http://{request.META["HTTP_HOST"]}/users/auth/\n'
                              f'Пожалуйста, свяжитесь с нами, если это были не вы.',
                              'test_gym@list.ru', [form.cleaned_data['email']],
                              fail_silently=False)
                    return HRR('/users/auth/')
                else:
                    return render(request, 'restore.html', {
                        'rest_form': form,
                        'header': 'Аккаунта с данным адресом почты не существует'})
            else:
                return render(request, 'signup.html', {'reg_form': form, 'header': 'Капча неверна, попробуйте еще раз'})
        else:
            return render(request, 'restore.html', {
                'rest_form': form,
                'header': 'Проверьте правильность введнных данных и попробуйте еще раз'})


def log_out(request):
    logout(request)
    return HRR('/')


def user_change(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, 'user_change.html', {'edit_form': UserEditForm})
        else:
            return render(request, 'log_must_error.html')

    elif request.method == 'POST':
        if request.user.is_authenticated:
            form = UserEditForm(request.POST)
            if form.is_valid():
                status = user_edit_form_valid(form.cleaned_data)
                if type(status) is bool:
                    user = request.user
                    user.entity = form.cleaned_data['entity']
                    user.phone = form.cleaned_data['phone']
                    user.name = form.cleaned_data['name']
                    user.soname = form.cleaned_data['soname']
                    user.save()
                    return HRR(f'/users/user/{user.id}')
                else:
                    return render(request, 'user_change.html', {'edit_form': form, 'header': status})
            else:
                return render(request, 'user_change.html', {
                    'edit_form': form,
                    'header': 'Пожалуйста, проверьте правильность введенных данных и попробуйте еще раз'})
        else:
            return render(request, 'log_must_error.html')


def make_admin(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            if request.user.is_staff:
                form = UserUpToAdminForm(request.POST)
                if form.is_valid():
                    some_user_id = int(form.cleaned_data['sid'])
                    some_user = CustomUser.objects.get(id=some_user_id)
                    some_user.is_staff = True
                    some_user.save()
                    return HRR(f'/users/user/{some_user_id}/')
            else:
                return render(request, 'permission_deny_error.html')
        else:
            return render(request, 'log_must_error.html')
