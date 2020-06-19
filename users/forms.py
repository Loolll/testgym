from django import forms


class UserCreationForm(forms.Form):
    password1 = forms.CharField(label='Пароль:', widget=forms.PasswordInput, min_length=6, max_length=50)
    password2 = forms.CharField(label='Повторите пароль:', widget=forms.PasswordInput, min_length=6, max_length=50)
    captcha = forms.CharField(widget=forms.HiddenInput, required=False)  # TODO on deploy
    email = forms.EmailField(label='Email:', required=True)
    name = forms.CharField(label='Имя:', required=True, max_length=100)
    soname = forms.CharField(label='Фамилия:', required=True, max_length=100)
    phone = forms.CharField(label='Телефон:', required=True, max_length=15)
    entity = forms.BooleanField(label='Я - представитель юридического лица или ИП', required=False)


class UserAuthForm(forms.Form):
    password = forms.CharField(label='Пароль:', required=True, widget=forms.PasswordInput, min_length=6, max_length=50)
    email = forms.EmailField(label='Email:', required=True)


class UserRestoreForm(forms.Form):
    email = forms.EmailField(label='Email', required=True)
    captcha = forms.CharField(widget=forms.HiddenInput, required=False)  # TODO on deploy


class UserEditForm(forms.Form):
    name = forms.CharField(label='Имя:', required=True, max_length=100)
    soname = forms.CharField(label='Фамилия:', required=True, max_length=100)
    phone = forms.CharField(label='Телефон:', required=True, max_length=15)
    entity = forms.BooleanField(label='Я - представитель юридического лица или ИП', required=False)


class UserUpToAdminForm(forms.Form):
    sid = forms.CharField(required=True, max_length=100, widget=forms.HiddenInput)
