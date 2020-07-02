from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.generic import DetailView
from .models import Product, Category, Rates
from random import randint


class ProductView(DetailView):
    model = Product
    context_object_name = 'product'

    def get_object(self):
        obj = super().get_object()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rid = [cat.id for cat in Category.objects.all()]
        context['recommendations'] = Product.objects.filter(
            category=Category.objects.get(id=rid[randint(0, len(rid)-1)]))[:9]
        rates = Rates.objects.filter(product=self.object)
        try:
            context['rate'] = sum([x.rate for x in rates])/len(rates)
        except ZeroDivisionError:
            context['rate'] = -1
        context['rate_count'] = len(rates)
        return context


urlpatterns = [
    path('', views.index),
    path('add/', views.add),
    path('add/product/', views.add_product),
    path('add/brand/', views.add_brand),
    path('add/category/', views.add_category),
    path('permission_deny/', views.permission_deny),
    path('args_error/', views.args_error),
    path('product/<int:pk>/', ProductView.as_view(template_name='product.html')),
    path('product/delete/', views.delete_product),
    path('product/edit/', views.edit_product),
    path('mycart/change_count/', views.my_cart_change_count),
    path('add/in/', views.add_in_cart_or_favorite),
    path('mycart/', views.my_cart),
    path('myfavorites/', views.my_favorites),
    path('myfavorites/delete/', views.delete_from_favorites),
    path('mycart/pay/', views.my_cart),
    path('product/rate/', views.rate_product),
]
