from django.db import models
from users.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField(max_length=150, verbose_name='Название')
    description = models.CharField(max_length=1000, verbose_name='Описание')
    price = models.IntegerField(verbose_name='Стоимость')
    count = models.IntegerField(verbose_name='Колличество')
    discount = models.IntegerField(verbose_name='Стоимость по скидке', default=-1)
    imgpath = models.CharField(max_length=1000, verbose_name='Путь к картинке')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='Бренд')

    def __str__(self):
        return self.name


class Favorites(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    ip = models.CharField(verbose_name='IP анонимного клиента', max_length=16, default='')
    count = models.IntegerField(verbose_name='Колличество', default=1)

    def __str__(self):
        return self.product.name


class Carts(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    ip = models.CharField(verbose_name='IP анонимного клиента', max_length=16, default='')
    count = models.IntegerField(verbose_name='Колличество', default=1)

    def __str__(self):
        return self.product.name