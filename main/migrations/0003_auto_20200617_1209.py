# Generated by Django 3.0.7 on 2020-06-17 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_product_brand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.IntegerField(default=-1, verbose_name='Стоимость по скидке'),
        ),
    ]
