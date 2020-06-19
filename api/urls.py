from django.urls import path, include
from . import views
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt


router = routers.DefaultRouter()


urlpatterns = [
    path('UserCreate/', csrf_exempt(views.user_create)),
    path('UserEdit/', csrf_exempt(views.user_edit)),
    path('BrandCreate/', csrf_exempt(views.brand_add)),
    path('BrandRename/', csrf_exempt(views.brand_edit)),
    path('BrandDelete/', csrf_exempt(views.brand_delete)),
    path('BrandsGet/', csrf_exempt(views.brands_get)),
    path('CategoryCreate/', csrf_exempt(views.category_add)),
    path('CategoryRename/', csrf_exempt(views.category_edit)),
    path('CategoryDelete/', csrf_exempt(views.category_delete)),
    path('CategoriesGet/', csrf_exempt(views.categories_get)),
    path('ProductsGet/', csrf_exempt(views.products_get)),
    path('ProductDelete/', csrf_exempt(views.product_delete)),
    path('ProductEdit/', csrf_exempt(views.product_edit)),
    path('ProductCreate/', csrf_exempt(views.product_create)),
    path('CartGet/', csrf_exempt(views.cart_view)),
    path('CartChange/', csrf_exempt(views.cart_change)),
    path('CartAdd/', csrf_exempt(views.cart_add)),
    path('FavoriteGet/', csrf_exempt(views.favorite_view)),
    path('FavoriteDelete/', csrf_exempt(views.favorite_delete)),
    path('FavoriteAdd/', csrf_exempt(views.favorite_add)),
]
