from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication
from django.http import JsonResponse
from django.contrib.auth import authenticate, logout, login
from rest_framework.permissions import IsAuthenticated
from .auth import CsrfExemptSessionAuthentication, api_user_authentication
from users.models import CustomUser
from main.models import Brand, Category, Product, Carts, Favorites
from contextlib import suppress, contextmanager
from django.conf import settings
from main.views import handle_uploaded_product, get_client_ip


def user_creation_form_valid(data):
    try:
        password = data['password']
    except:
        return 'Пароль отсутствует'

    try:
        if not all([x in "+0123456789" for x in data['phone']]):
            return 'Введите правильный номер телефона'
    except:
        return 'Введите правильный номер телефона'

    try:
        if not all([x.lower() in 'abcdefghijklmnopqrstuvwyxzабвгдеёжзийклмнопрстуфхцчшщъыьэюя' for x in data['name']]):
            return 'Имя введено некорректно'
    except:
        return 'Имя введено некорректно'

    try:
        if not all([x.lower() in 'abcdefghijklmnopqrstuvwyxzабвгдеёжзийклмнопрстуфхцчшщъыьэюя' for x in data['soname']]):
            return 'Фамилия введена некорректно'
    except:
        return 'Фамилия введена некорректно'

    try:
        if len(CustomUser.objects.filter(email=data['email'])):
            return 'Аккаунт на данный email уже зарегистрирован'
    except:
        return 'Аккаунт на данный email уже зарегистрирован'
    return True


def user_edit_form_valid(data):
    with suppress(Exception):
        if not all([x in "+0123456789" for x in data['phone']]):
            return 'Введите правильный номер телефона'

    with suppress(Exception):
        if not all([x.lower() in 'abcdefghijklmnopqrstuvwyxzабвгдеёжзийклмнопрстуфхцчшщъыьэюя' for x in data['name']]):
            return 'Имя введено некорректно'

    with suppress(Exception):
        if not all(
                [x.lower() in 'abcdefghijklmnopqrstuvwyxzабвгдеёжзийклмнопрстуфхцчшщъыьэюя' for x in data['soname']]):
            return 'Фамилия введена некорректно'

    return True


def product_edit_form_valid(data):
    with suppress(Exception):
        category_id = data['category_id']
        try:
            category = Category.objects.get(id=category_id)
        except:
            return 'Указанной категории не существует'

    with suppress(Exception):
        brand_id = data['brand_id']
        try:
            brand = Brand.objects.get(id=brand_id)
        except:
            return 'Указанного бренда не существует'

    with suppress(Exception):
        if len(data['name']) > 149:
            return 'Имя слишком длинное'

    with suppress(Exception):
        if len(data['description']) > 1000:
            return 'Описание слишком длинное'

    with suppress(Exception):
        if not all([x.lower() in '0123456789' for x in data['price']]):
            return 'Цена содерждит запрещенные символы'

    with suppress(Exception):
        if not all([x.lower() in '0123456789' for x in data['discount']]):
            return 'Скидка содерждит запрещенные символы'

    with suppress(Exception):
        if not all([x.lower() in '0123456789' for x in data['count']]):
            return 'Кол-во содерждит запрещенные символы'

    return True


def product_create_form_valid(data):
    try:
        category = Category.objects.get(id=data['category_id'])
    except:
        return 'Указанной категории не существует'

    try:
        brand = Brand.objects.get(id=data['brand_id'])
    except:
        return 'Указанного бренда не существует'

    try:
        if len(data['name']) > 149:
            return 'Имя слишком длинное'
    except:
        return 'Имя не указано'

    try:
        if len(data['description']) > 1000:
            return 'Описание слишком длинное'
    except:
        return "Описание не указано"

    try:
        if not all([x.lower() in '0123456789' for x in data['price']]):
            return 'Цена содерждит запрещенные символы'
    except:
        return "Цена не указана"

    with suppress(Exception):
        if not all([x.lower() in '-0123456789' for x in data['discount']]):
            return 'Скидка содерждит запрещенные символы'

    try:
        if not all([x.lower() in '0123456789' for x in data['count']]):
            return 'Кол-во содерждит запрещенные символы'
    except:
        return "Кол-во товара не указано"

    return True


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication, BasicAuthentication])
def user_create(request):
    if request.method == 'POST':
        status = user_creation_form_valid(request.POST)
        if type(status) is bool:
            email = request.POST['email']
            password = request.POST['password']
            name = request.POST['name']
            soname = request.POST['soname']
            phone = request.POST['phone']
            entity = request.POST['entity'].lower() == 'true'
            user = CustomUser.objects.create(name=name, soname=soname, phone=phone,
                                             password=password, entity=entity, email=email)
            user.set_password(password)
            user.save()
        return JsonResponse({'Status': 'Created' if type(status) is bool else status})


@api_view(['PUT'])
@authentication_classes([CsrfExemptSessionAuthentication])
def user_edit(request):
    if request.method == 'PUT':
        user = api_user_authentication(request)
        if user is not None:
            status = user_edit_form_valid(request.POST)
            if type(status) is bool:
                with suppress(Exception):
                    user.phone = request.POST['phone']
                with suppress(Exception):
                    user.name = request.POST['name']
                with suppress(Exception):
                    user.soname = request.POST['soname']
                with suppress(Exception):
                    user.entity = request.POST['entity'].lower() == 'true'
                user.save()

        else:
            status = 'Аутентификационные данные неверны'

        return JsonResponse({'Status': 'Edited' if type(status) is bool else status})


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def brand_add(request):
    if request.method == 'POST':
        user = api_user_authentication(request)
        if user is not None:
            if user.is_staff:
                try:
                    name = request.POST['name']
                    Brand.objects.create(name=name)
                    status = True
                except:
                    status = 'Укажите имя для бренда'
            else:
                status = 'Недостаточно прав'
        else:
            status = 'Аутентификационные данные неверны'

        return JsonResponse({'Status': 'Created' if type(status) is bool else status})


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def category_add(request):
    if request.method == 'POST':
        user = api_user_authentication(request)
        if user is not None:
            if user.is_staff:
                try:
                    name = request.POST['name']
                    Category.objects.create(name=name)
                    status = True
                except:
                    status = 'Укажите имя для категории'
            else:
                status = 'Недостаточно прав'
        else:
            status = 'Аутентификационные данные неверны'

        return JsonResponse({'Status': 'Created' if type(status) is bool else status})


@api_view(['PUT'])
@authentication_classes([CsrfExemptSessionAuthentication])
def category_edit(request):
    if request.method == 'PUT':
        user = api_user_authentication(request)
        if user is not None:
            if user.is_staff:
                try:
                    category_id = request.POST['id']
                    category = Category.objects.get(id=category_id)
                    try:
                        name = request.POST['name']
                        category.name = name
                        category.save()
                        status = True
                    except:
                        status = 'Укажите новое имя для категории'
                except:
                    status = 'Укажите корректный id для категории'
            else:
                status = 'Недостаточно прав'
        else:
            status = 'Аутентификационные данные неверны'

        return JsonResponse({'Status': 'Renamed' if type(status) is bool else status})


@api_view(['PUT'])
@authentication_classes([CsrfExemptSessionAuthentication])
def brand_edit(request):
    if request.method == 'PUT':
        user = api_user_authentication(request)
        if user is not None:
            if user.is_staff:
                try:
                    brand_id = request.POST['id']
                    brand = Brand.objects.get(id=brand_id)
                    try:
                        name = request.POST['name']
                        brand.name = name
                        brand.save()
                        status = True
                    except:
                        status = 'Укажите новое имя для бренда'
                except:
                    status = 'Укажите корректный id для бренда'
            else:
                status = 'Недостаточно прав'
        else:
            status = 'Аутентификационные данные неверны'

        return JsonResponse({'Status': 'Renamed' if type(status) is bool else status})


@api_view(['DELETE'])
@authentication_classes([CsrfExemptSessionAuthentication])
def category_delete(request):
    if request.method == 'DELETE':
        user = api_user_authentication(request)
        if user is not None:
            if user.is_staff:
                try:
                    category_id = request.POST['id']
                    Category.objects.get(id=category_id).delete()
                    status = True
                except:
                    status = 'Укажите существующий id для категории'
            else:
                status = 'Недостаточно прав'
        else:
            status = 'Аутентификационные данные неверны'

        return JsonResponse({'Status': 'Deleted' if type(status) is bool else status})


@api_view(['DELETE'])
@authentication_classes([CsrfExemptSessionAuthentication])
def brand_delete(request):
    if request.method == 'DELETE':
        user = api_user_authentication(request)
        if user is not None:
            if user.is_staff:
                try:
                    brand_id = request.POST['id']
                    Brand.objects.get(id=brand_id).delete()
                    status = True
                except:
                    status = 'Укажите существующий id для бренда'
            else:
                status = 'Недостаточно прав'
        else:
            status = 'Аутентификационные данные неверны'

        return JsonResponse({'Status': 'Deleted' if type(status) is bool else status})


@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
def categories_get(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        result = dict([category.id, category.name] for category in categories)
        return JsonResponse(result)


@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
def brands_get(request):
    if request.method == 'GET':
        brands = Brand.objects.all()
        result = dict([brand.id, brand.name] for brand in brands)
        return JsonResponse(result)


@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
def products_get(request):
    if request.method == 'GET':
        products = Product.objects.all()
        result = dict([product.id, {'Name': product.name, 'Description': product.description,
                                    'Category': product.category.name, 'CategoryID': product.category.id,
                                    'Count': product.count,
                                    'Brand': product.brand.name, 'BrandID': product.brand.id,
                                    'Price': product.price,
                                    'ImagePath': settings.MEDIA_ROOT+ '\\'+ product.imgpath + '.png',
                                    'Discount': product.discount}]for product in products)
        return JsonResponse(result)


@api_view(['DELETE'])
@authentication_classes([CsrfExemptSessionAuthentication])
def product_delete(request):
    if request.method == 'DELETE':
        user = api_user_authentication(request)
        if user is not None:
            if user.is_staff:
                try:
                    product_id = request.POST['id']
                    Product.objects.get(id=product_id).delete()
                    status = True
                except:
                    status = 'Укажите существующий id для товара'
            else:
                status = 'Недостаточно прав'
        else:
            status = 'Аутентификационные данные неверны'

        return JsonResponse({'Status': 'Deleted' if type(status) is bool else status})


@api_view(['PUT'])
@authentication_classes([CsrfExemptSessionAuthentication])
def product_edit(request):
    if request.method == 'PUT':
        user = api_user_authentication(request)
        if user is not None:
            if user.is_staff:
                try:
                    product_id = request.POST['id']
                    product = Product.objects.get(id=product_id)
                    status = product_edit_form_valid(request.POST)
                    if type(status) is bool:
                        with suppress(Exception):
                            product.name = request.POST['name']
                        with suppress(Exception):
                            product.price = request.POST['price']
                        with suppress(Exception):
                            product.discount = request.POST['discount']
                        with suppress(Exception):
                            product.description = request.POST['description']
                        with suppress(Exception):
                            product.count = request.POST['count']
                        with suppress(Exception):
                            product.category = Category.objects.get(id=request.POST['category_id'])
                        with suppress(Exception):
                            product.brand = Brand.objects.get(id=request.POST['brand_id'])

                        product.save()
                        with suppress(Exception):
                            file = request.FILES['photo']
                            if file is not None:
                                handle_uploaded_product(file, product.imgpath)
                except:
                    status = 'Укажите корректный id для товара'
            else:
                status = 'Недостаточно прав'
        else:
            status = 'Аутентификационные данные неверны'

        return JsonResponse({'Status': 'Edited' if type(status) is bool else status})


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def product_create(request):
    if request.method == 'POST':
        user = api_user_authentication(request)
        if user is not None:
            if user.is_staff:
                status = product_create_form_valid(request.POST)
                if type(status) is bool:
                    name = request.POST['name']
                    price = request.POST['price']
                    try:
                        discount = request.POST['discount']
                    except:
                        discount = -1
                    description = request.POST['description']
                    count = request.POST['count']
                    category = Category.objects.get(id=request.POST['category_id'])
                    brand = Brand.objects.get(id=request.POST['brand_id'])
                    try:
                        file = request.FILES['photo']
                        if file is not None:
                            product = Product.objects.create(name=name, price=price, discount=discount,
                                                             description=description, count=count, category=category,
                                                             brand=brand)
                            product.imgpath = product.id
                            product.save()
                            handle_uploaded_product(file, product.imgpath)
                    except:
                        status = 'Изображение товара не указано'


            else:
                status = 'Недостаточно прав'
        else:
            status = 'Аутентификационные данные неверны'

        return JsonResponse({'Status': 'Created' if type(status) is bool else status})


@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
def cart_view(request):
    user = api_user_authentication(request)
    carts: list
    if user is not None:
        carts = Carts.objects.filter(user=user)
    else:
        carts = Carts.objects.filter(ip=get_client_ip(request))
    result = dict([cart.id, {'Product': cart.product.name, "ProductID": cart.product.id,
                             'Count': cart.count}] for cart in carts)
    return JsonResponse(result)


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def cart_change(request):
    user = api_user_authentication(request)
    try:
        count = int(request.POST['count'])
        try:
            cart = Carts.objects.get(id=request.POST['id'])
            if user is not None:
                if cart.user == user:
                    if count != 0:
                        cart.count = count
                        cart.save()
                        status = 'Changed'
                    else:
                        cart.delete()
                        status = 'Deleted'
                else:
                    status = 'Отказано в доступе'
            else:
                if cart.ip == get_client_ip(request):
                    if count != 0:
                        cart.count = count
                        cart.save()
                        status = 'Changed'
                    else:
                        cart.delete()
                        status = 'Deleted'
        except:
            status = 'Введите корректный id корзины'
    except:
        status = 'Введите число'
    return JsonResponse({'Status': status})


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def cart_add(request):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=request.POST['product_id'])
            user = api_user_authentication(request)
            if user is not None:
                if not len(Carts.objects.filter(user=user, product=product)):
                    Carts.objects.create(user=user, product=product, count=1)
                    status = 'Added'
                else:
                    status = 'Уже существует такой товар в корзине'
            else:
                anonym = CustomUser.objects.get(id=3)
                if not len(Carts.objects.filter(user=anonym, ip=get_client_ip(request), product=product)):
                    Carts.objects.create(user=anonym, ip=get_client_ip(request),
                                         product=product, count=1)
                    status = 'Added'
                else:
                    status = 'Уже существует такой товар в корзине'
        except:
            status = 'Укажите корректный id товара'

        return JsonResponse({"status": status})


@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication])
def favorite_view(request):
    user = api_user_authentication(request)
    favorites: list
    if user is not None:
        favorites = Favorites.objects.filter(user=user)
    else:
        favorites = Favorites.objects.filter(ip=get_client_ip(request))
    result = dict([favorite.id, {
        'Product': favorite.product.name, "ProductID": favorite.product.id}] for favorite in favorites)
    return JsonResponse(result)


@api_view(['DELETE'])
@authentication_classes([CsrfExemptSessionAuthentication])
def favorite_delete(request):
    user = api_user_authentication(request)
    try:
        favorite = Favorites.objects.get(id=request.POST['id'])
        if user is not None:
            if favorite.user == user:
                favorite.delete()
                status = 'Deleted'
            else:
                status = 'Отказано в доступе'
        else:
            if favorite.ip == get_client_ip(request):
                favorite.delete()
                status = 'Deleted'
    except:
        status = 'Введите корректный id избранного'
    return JsonResponse({'Status': status})


@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def favorite_add(request):
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=request.POST['product_id'])
            user = api_user_authentication(request)
            if user is not None:
                if not len(Favorites.objects.filter(user=user, product=product)):
                    Favorites.objects.create(user=user, product=product, count=1)
                    status = 'Added'
                else:
                    status = 'Уже существует такой товар в избранном'
            else:
                anonym = CustomUser.objects.get(id=3)
                if not len(Favorites.objects.filter(user=anonym, ip=get_client_ip(request), product=product)):
                    Favorites.objects.create(user=anonym, ip=get_client_ip(request),
                                         product=product, count=1)
                    status = 'Added'
                else:
                    status = 'Уже существует такой товар в избранном'
        except:
            status = 'Укажите корректный id товара'

        return JsonResponse({"status": status})
