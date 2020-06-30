from django import forms
from .models import Product


class CategoryAddForm(forms.Form):
    name_category = forms.CharField(required=True, max_length=150, label='Название:', min_length=1)


class ProductAddForm(forms.ModelForm):
    photo = forms.FileField(label='Изображение', required=True)
    description = forms.CharField(label='Описание', required=True, max_length=1000, widget=forms.Textarea)

    class Meta:
        model = Product
        fields = ['category', 'brand', 'name', 'price', 'count', 'discount']


class ProductEditForm(forms.ModelForm):
    photo = forms.FileField(label='Новое изображение', required=False)
    id = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Product
        fields = ['category', 'brand', 'name', 'description', 'price', 'count', 'discount']


class BrandAddForm(forms.Form):
    name_brand = forms.CharField(required=True, max_length=150, label='Название:', min_length=1)


class PayOldUserForm(forms.Form):
    cc_number = forms.CharField(label='Номер карты', min_length=16, max_length=16)
    cc_expiry = forms.CharField(label='Срок действия', min_length=5, max_length=5)
    cc_code = forms.CharField(label='CVV/CVC', min_length=3, max_length=3)
    cc_name = forms.CharField(label='Имя', max_length=1000)


class PayNewUserForm(PayOldUserForm):
    password = forms.CharField(label='Пароль:', widget=forms.PasswordInput, min_length=6, max_length=50)
    email = forms.EmailField(label='Email:', required=True)
    name = forms.CharField(label='Имя:', required=True, max_length=100)
    soname = forms.CharField(label='Фамилия:', required=True, max_length=100)
    phone = forms.CharField(label='Телефон:', required=True, max_length=15)
    entity = forms.BooleanField(label='Я - представитель юридического лица или ИП', required=False)

    cc_number = forms.CharField(label='Номер карты', min_length=16, max_length=16)
    cc_expiry = forms.CharField(label='Срок действия', min_length=5, max_length=5)
    cc_code = forms.CharField(label='CVV/CVC', min_length=3, max_length=3)
    cc_name = forms.CharField(label='Имя', max_length=1000)
