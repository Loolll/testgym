from django.shortcuts import render
from .models import Category, Brand, Product, Carts, Favorites
from users.models import CustomUser
from .forms import CategoryAddForm, BrandAddForm, ProductAddForm, PayNewUserForm, PayOldUserForm, ProductEditForm
from django.http import HttpResponseRedirect as HRR
from django.conf import settings
from django.core import exceptions
import datetime
from django.utils.datastructures import MultiValueDictKeyError


def default_include_undefined_for_get_request(request, parameter, default):
    result = request.GET.get(parameter, 'undefined')
    if result == "" or result == " ":
        result = 'undefined'
    return result if result != 'undefined' else default


def user_creation_form_valid(data):  # Does not used include from users.views, because here we have only one password
    if not all([x in "+0123456789" for x in data['phone']]):
        return 'Введите правильный номер телефона'
    if not all([x.lower() in 'abcdefghijklmnopqrstuvwyxzабвгдеёжзийклмнопрстуфхцчшщъыьэюя' for x in data['name']]):
        return 'Имя введено некорректно'
    if not all([x.lower() in 'abcdefghijklmnopqrstuvwyxzабвгдеёжзийклмнопрстуфхцчшщъыьэюя' for x in data['soname']]):
        return 'Фамилия введена некорректно'
    if len(CustomUser.objects.filter(email=data['email'])):
        return 'Аккаунт на данный email уже зарегистрирован'
    return True


def card_validation(data):
    if not all([x.lower() in 'abcdefghijklmnopqrstuvwxyz' for x in data['cc_name']]):
        return 'Проверьте правильность введного имени карты и попробуйте еще раз'
    if not all([x in '0123456789' for x in data['cc_number']]):
        return 'Проверьте правильность введного номера карты и попробуйте еще раз'
    if not all([x in '0123456789' for x in data['cc_code']]):
        return 'Проверьте правильность введного CVV/CVC карты и попробуйте еще раз'
    month, year = data['cc_expiry'].split('/')
    if int(year) < datetime.datetime.now().year % 100:
        return 'Проверьте правильность введной даты карты и попробуйте еще раз'
    if int(year) == datetime.datetime.now().year % 100:
        if int(month) < datetime.datetime.now().month:
            return 'Проверьте правильность введной даты карты и попробуйте еще раз'
    return True


def permission_deny(request):
    return render(request, 'permission_deny.html')


def args_error(request):
    return render(request, 'args_error.html')


def handle_uploaded_product(file, path):
    with open(f"{settings.MEDIA_ROOT}/products/{path}.png", 'wb+') as destinatiion:
        for chunk in file.chunks():
            destinatiion.write(chunk)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def index(request):
    if request.method == 'GET':
        # Processing of getting GET parameters
        categories = Category.objects.all()
        brands = Brand.objects.all()
        category_id = default_include_undefined_for_get_request(request, 'category', -1)
        brand_id = default_include_undefined_for_get_request(request, 'brand', -1)
        min_price = default_include_undefined_for_get_request(request, 'min_price', -1)
        max_price = default_include_undefined_for_get_request(request, 'max_price', -1)
        min_count = default_include_undefined_for_get_request(request, 'min_count', -1)
        max_count = default_include_undefined_for_get_request(request, 'max_count', -1)
        discount = default_include_undefined_for_get_request(request, 'discount', 'False') == 'True'
        search = default_include_undefined_for_get_request(request, 'search', '')
        group_id = int(default_include_undefined_for_get_request(request, 'group_by', -1))

        # Processing of filters which include using GET parameters
        products = Product.objects.all()  # 0) Getting
        if category_id != -1:  # 1) Filter by category
            products = products.filter(category=categories.get(id=category_id))
        if brand_id != -1:  # 2) Filter by brand
            products = products.filter(brand=brands.get(id=brand_id))
        if min_price != -1:  # 3) Filter by min_price
            products = products.filter(price__gte=min_price)
        if max_price != -1:  # 4) Filter by max_price
            products = products.filter(price__lte=max_price)
        if min_count != -1:  # 5) Filter by min_count
            products = products.filter(count__gte=min_count)
        if max_count != -1:  # 6) Filter by max_count
            products = products.filter(count__lte=max_count)
        if discount:  # 7) Filter items without discount
            products = products.filter(discount__gt=-1)

        # Grouping
        if group_id == -1:
            products = products.order_by('-id')
        elif group_id == 0:
            products = products.order_by('price')
        elif group_id == 1:
            products = products.order_by('-price')
        elif group_id == 2:
            products = products.order_by('count')
        elif group_id == 3:
            products = products.order_by('-count')
        elif group_id == 5:
            pass  # Default (by id incr)

        # Searching
        final_products = []
        if search != '':  # 8) Filter by search result
            included_words = set([word.lower() for word in search.split(' ')])
            for product in products:
                count = 0
                for word in product.name.split(' '):
                    if word.lower() in included_words:
                        count += 1
                for word in product.description.split(' '):
                    if word.lower() in included_words:
                        count += 1
                final_products.append([count, product])
            products = sorted(final_products, key=lambda product: product[0])
            products = [product[1] for product in products if product[0]]

        return render(request, 'index.html', {
            'categories': categories,
            'brands': brands,
            'category_id': category_id,
            'brand_id': brand_id,
            'group_id': group_id,
            'products': products,
        })


def add(request):
    if request.method == 'GET':
        if request.user.is_staff:
            return render(request, 'add.html', {
                'category_add_form': CategoryAddForm, 'brand_add_form': BrandAddForm, 'product_add_form': ProductAddForm})
        else:
            return HRR('/permission_deny/')


def add_product(request):
    if request.method == 'POST':
        if request.user.is_staff:
            form = ProductAddForm(request.POST, request.FILES)
            if form.is_valid():
                name = form.cleaned_data['name']
                category = form.cleaned_data['category']
                brand = form.cleaned_data['brand']
                count = form.cleaned_data['count']
                discount = form.cleaned_data['discount']
                description = form.cleaned_data['description']
                price = form.cleaned_data['price']
                product = Product.objects.create(name=name, category=category, brand=brand, description=description,
                                                 count=count, discount=discount, price=price)
                product.imgpath = product.id
                product.save()
                photo = request.FILES['photo']
                handle_uploaded_product(photo, product.imgpath)
                return HRR('/add')
            else:
                return render(request, 'add_error.html', {
                    'header': 'Проверьте правильность введенных данных и попробуйте еще раз'})
        else:
            return HRR('/permission_deny/')


def delete_product(request):
    if request.user.is_staff:
        product_id = default_include_undefined_for_get_request(request, 'id', -1)
        if len(Product.objects.filter(id=product_id)):
            Product.objects.get(id=product_id).delete()
            return HRR('/')
        else:
            return HRR('/args_error/')
    else:
        return HRR('/permission_deny/')


def edit_product(request):
    if request.user.is_staff:
        if request.method == 'GET':
            product_id = default_include_undefined_for_get_request(request, 'id', -1)
            if len(Product.objects.filter(id=product_id)):
                product = Product.objects.get(id=product_id)
                form = ProductEditForm(instance=product)
                return render(request, 'product_edit.html', {'edit_form': form, 'id': product_id})
            else:
                return HRR('/args_error/')
        elif request.method == 'POST':
            form = ProductEditForm(request.POST, request.FILES)
            if form.is_valid():
                product_id = form.cleaned_data['id']
                try:
                    product = Product.objects.get(id=product_id)
                    product.name = form.cleaned_data['name']
                    product.category = form.cleaned_data['category']
                    product.brand = form.cleaned_data['brand']
                    product.count = form.cleaned_data['count']
                    product.discount = form.cleaned_data['discount']
                    product.description = form.cleaned_data['description']
                    product.price = form.cleaned_data['price']
                    product.save()
                    try:
                        if request.FILES['photo'] is not None:
                            photo = request.FILES['photo']
                            handle_uploaded_product(photo, product.imgpath)
                            print('ok------------')
                    except MultiValueDictKeyError:
                        pass
                    return HRR(f'/product/{product_id}')
                except exceptions.ObjectDoesNotExist:
                    return HRR('/args_error/')
            else:
                return render(request, 'add_error.html', {
                    'header': 'Проверьте правильность введенных данных и попробуйте еще раз'})
    else:
        return HRR('/permission_deny/')


def add_brand(request):
    if request.method == 'POST':
        if request.user.is_staff:
            form = BrandAddForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name_brand']
                Brand.objects.create(name=name)
                return HRR('/add')
            else:
                return render(request, 'add_error.html', {
                    'header': 'Проверьте правильность введенных данных и попробуйте еще раз'})
        else:
            return HRR('/permission_deny/')


def add_category(request):
    if request.method == 'POST':
        if request.user.is_staff:
            form = CategoryAddForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name_category']
                Category.objects.create(name=name)
                return HRR('/add')
            else:
                return render(request, 'add_error.html', {
                    'header': 'Проверьте правильность введенных данных и попробуйте еще раз'})
        else:
            return HRR('/permission_deny/')


def add_in_cart_or_favorite(request):
    """ Here, I use many times filter() instead the get() method, because in get,
     if object does not exist it returns exception."""
    if request.method == 'GET':
        where = default_include_undefined_for_get_request(request, 'in', None)
        if where is not None:
            product_id = default_include_undefined_for_get_request(request, 'id', None)
            if product_id is not None:
                if len(Product.objects.filter(id=product_id)):
                    product = Product.objects.filter(id=product_id)[0]
                    if request.user.is_authenticated:
                        if where == 'cart':
                            if len(Carts.objects.filter(product=product, user=request.user)):
                                cart = Carts.objects.get(product=product, user=request.user)
                                cart.count += 1
                                cart.save()
                            else:
                                Carts.objects.create(product=product, count=1, user=request.user)
                        if where == 'star':
                            if len(Favorites.objects.filter(product=product, user=request.user)):
                                favorite = Favorites.objects.get(product=product, user=request.user)
                                favorite.count += 1
                                favorite.save()
                            else:
                                Favorites.objects.create(product=product, user=request.user, count=1)
                    else:
                        ip = get_client_ip(request)
                        anonym = CustomUser.objects.get(id=3)
                        if where == 'cart':
                            if len(Carts.objects.filter(product=product, user=anonym, ip=ip)):
                                cart = Carts.objects.get(product=product, user=anonym, ip=ip)
                                cart.count += 1
                                cart.save()
                            else:
                                Carts.objects.create(product=product, count=1, user=anonym, ip=ip)
                        if where == 'star':
                            if len(Favorites.objects.filter(product=product, user=anonym, ip=ip)):
                                favorite = Favorites.objects.get(product=product, user=anonym, ip=ip)
                                favorite.count += 1
                                favorite.save()
                            else:
                                Favorites.objects.create(product=product, user=anonym, ip=ip, count=1)
                    url = default_include_undefined_for_get_request(request, 'from', '/')
                    return HRR(url.replace('~', '?').replace('№', '&'))
            else:
                return HRR('/args_error/')
        return HRR('/args_error/')


def my_cart(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            carts = Carts.objects.filter(user=request.user)
            form = PayOldUserForm
        else:
            carts = Carts.objects.filter(ip=get_client_ip(request))
            form = PayNewUserForm
        total_with_discount = sum([
            x.product.price * x.count if x.product.discount == -1 else x.product.discount * x.count for x in carts])
        total_without_discount = sum([x.product.price * x.count for x in carts])

        return render(request, 'cart_view.html', {
            'carts': carts, 'total_with_discount': total_with_discount,
            'total_without_discount': total_without_discount, 'pay_form': form})
    elif request.method == 'POST':
        if request.user.is_authenticated:
            form = PayOldUserForm(request.POST)
            if form.is_valid():
                status = card_validation(form.cleaned_data)
                if type(status) is bool:
                    # Wrapper for card
                    # cc_number = form.cleaned_data['cc_number']
                    # cc_expire = form.cleaned_data['cc_expiry']
                    # cc_code = form.cleaned_data['cc_code']
                    # cc_name = form.cleaned_data['cc_name']

                    carts = Carts.objects.filter(user=request.user)
                    for cart in carts:
                        product = cart.product
                        product.count -= cart.count
                        product.save()
                    carts.delete()
                    return render(request, 'pay_ok.html', {
                        'header': 'Это страничка - заглушка, ее появление означает успешную оплату'})
                else:
                    return render(request, 'pay_error.html', {
                        'header': status})
            else:
                return render(request, 'pay_error.html', {
                    'header': 'Проверьте правильность введенных вами данных и попробуйте еще раз'})
        else:
            form = PayNewUserForm(request.POST)
            if form.is_valid():
                status = user_creation_form_valid(form.cleaned_data)
                if type(status) is bool:
                    status = card_validation(form.cleaned_data)
                    if type(status) is bool:
                        CustomUser.objects.create_user(email=form.cleaned_data['email'],
                                                       password=form.cleaned_data['password'],
                                                       phone=form.cleaned_data['phone'],
                                                       name=form.cleaned_data['name'],
                                                       soname=form.cleaned_data['soname'],
                                                       entity=form.cleaned_data['entity'])

                        # cc_number = form.cleaned_data['cc_number']
                        # cc_expire = form.cleaned_data['cc_expiry']
                        # cc_code = form.cleaned_data['cc_code']
                        # cc_name = form.cleaned_data['cc_name']

                        carts = Carts.objects.filter(ip=get_client_ip(request))
                        for cart in carts:
                            product = cart.product
                            product.count -= cart.count
                            product.save()
                        carts.delete()
                        return render(request, 'pay_ok.html', {
                            'header': 'Это страничка - заглушка, ее появление означает успешную оплату и регистрацию'})
                    else:
                        return render(request, 'pay_error.html', {
                            'header': status})
                else:
                    return render(request, 'pay_error.html', {
                        'header': status})
            else:
                return render(request, 'pay_error.html', {
                    'header': 'Проверьте правильность введенных вами данных и попробуйте еще раз'})


def my_cart_change_count(request):
    if request.method == 'GET':
        cart_id = default_include_undefined_for_get_request(request, 'id', -1)
        if cart_id != -1:
            count = int(default_include_undefined_for_get_request(request, 'count', -1))
            if count != 0:
                try:
                    cart = Carts.objects.get(id=cart_id)
                    if cart.user == request.user or cart.ip == get_client_ip(request):
                        cart.count = count
                        cart.save()
                        return HRR('/mycart/')
                    else:
                        return HRR('/permission_deny/')
                except exceptions.ObjectDoesNotExist:
                    return HRR('/args_error/')
            else:
                try:
                    cart = Carts.objects.get(id=cart_id)
                    if cart.user == request.user or cart.ip == get_client_ip(request):
                        cart.delete()
                        return HRR('/mycart/')
                    else:
                        return HRR('/permission_deny/')
                except exceptions.ObjectDoesNotExist:
                    return HRR('/args_error/')
        else:
            return HRR('/args_error/')


def my_favorites(request):
    if request.method == 'GET':
        favorites: list
        if request.user.is_authenticated:
            favorites = Favorites.objects.filter(user=request.user)
        else:
            favorites = Favorites.objects.filter(ip=get_client_ip(request))
        return render(request, 'favorites_view.html', {'favorites': favorites})


def delete_from_favorites(request):
    if request.method == 'GET':
        favorite_id = int(default_include_undefined_for_get_request(request, 'id', -1))
        if favorite_id > -1:
            if request.user.is_authenticated:
                try:
                    Favorites.objects.get(id=favorite_id, user=request.user).delete()
                except exceptions.ObjectDoesNotExist:
                    return HRR('/args_error/')
            else:
                try:
                    Favorites.objects.get(id=favorite_id, ip=get_client_ip(request)).delete()
                except exceptions.ObjectDoesNotExist:
                    return HRR('/args_error/')

            return HRR('/myfavorites/')
        else:
            return HRR('/args_error/')