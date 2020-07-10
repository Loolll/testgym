# Generated by Django 3.0.7 on 2020-07-09 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_rates'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount',
            field=models.FloatField(default=-1, verbose_name='Стоимость по скидке'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.FloatField(verbose_name='Стоимость'),
        ),
    ]