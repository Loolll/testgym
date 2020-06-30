from django.urls import path, include
from . import views
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt


router = routers.DefaultRouter()


urlpatterns = [
    path('Users/', csrf_exempt(views.users_view)),
    path('Brands/', csrf_exempt(views.brands_view)),
    path('Categories/', csrf_exempt(views.categories_view)),
    path('Products/', csrf_exempt(views.products_view)),
    path('Carts/', csrf_exempt(views.carts_view)),
    path('Favorites/', csrf_exempt(views.favorites_view)),
]
