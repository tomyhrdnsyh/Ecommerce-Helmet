from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import *
from django.db.models import Q
from django.shortcuts import redirect
from collections import defaultdict
from django.contrib import messages
from datetime import datetime, timedelta
import midtransclient
import uuid

# Create your views here.
SIZE_DICT = {'S': 'Small', 'L': 'Large', 'XL': 'Extra Large', 'XXL': 'Extra Extra Large'}


def index(request):
    context = {}

    # total product in cart
    context['total_in_cart'] = total_product_in_cart(request)

    # update status order
    if request.GET.get('status_code'):
        unique_code = request.GET.get('order_id')
        update_status_order = Order.objects.get(unique_code=unique_code)
        update_status_order.status = request.GET.get('transaction_status')
        update_status_order.updated_at = datetime.now()
        update_status_order.save()

    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


def pages(request):
    context = {}

    load_template = request.path.split('/')[-1]
    # MENU ADMIN
    if load_template == 'admin':
        return HttpResponseRedirect(reverse('admin:index'))

    # total product in cart
    context['total_in_cart'] = total_product_in_cart(request)

    # ====== check if any search ======
    if request.GET.get('q'):
        list_product = query_get_product(param=request.GET.get('q'))
        context['list_product'] = list_product
        load_template = 'shop.html'
    # ====== end check ======

    # ====== SHOP MENU ======

    if load_template == 'shop.html':
        # filtering
        context['type'] = Categories.objects.values('name')
        context['brands'] = Brands.objects.values('name')
        context['size'] = [{'code': item['name'], 'name': SIZE_DICT[item['name']]} for item in
                           Sizes.objects.values('name')]
        context['size_categories'] = SizeCategories.objects.values('name')

        if request.GET.get('type'):
            list_product = query_get_product(param=request.GET.get('type'), field='category__name')
        elif request.GET.get('brand'):
            list_product = query_get_product(param=request.GET.get('brand'), field='brand__name')
        elif request.GET.get('size'):
            list_product = query_get_product(param=request.GET.get('size'), field='size__name')
        elif request.GET.get('size_categories'):
            list_product = query_get_product(param=request.GET.get('size_categories'),
                                             field='size__size_category__name')
        else:
            list_product = query_get_product()
        context['list_product'] = list_product

        if request.GET.get('product_id'):

            # === insert product to cart model ===
            product_id = request.GET.get('product_id')
            try:
                cart = Cart.objects.get(product=product_id)
                update_cart_model(req=request, cart=cart, product=Products.objects.get(product_id=product_id))
                msg = 'Cart update success!'
            except Cart.DoesNotExist:
                product = Products.objects.get(product_id=product_id)
                add_to_cart_model(req=request, product=product)
                msg = 'Add to cart success!'

            # === end insert product ===
            messages.success(request, msg)

            return redirect('/shop.html')

    # ====== END SHOP MENU ======

    # ====== shop-single ======
    if load_template == 'shop-single.html':

        # delete session variable cart_id in shop-single page
        if request.session.get('cart_id'):
            del request.session['cart_id']

        if request.GET.get('name'):

            # General shop-single
            name_product = request.GET.get('name')
            context['name'] = name_product

            raw_detail = details_product(name_product)
            context.update(item_shop_single(raw_detail))

            # End general shop-single

            if request.GET.get('size'):
                for key, value in raw_detail.items():
                    if request.GET.get('size') in value.get('size'):
                        i = value.get('size').index(request.GET.get('size'))  # index of size
                        raw_detail_filter_size = {key: {key: [value[i]] for key, value in value.items()}}
                        context.update(item_shop_single(raw_detail_filter_size))

        if request.POST:
            if request.POST.get('buy'):
                request.session['id'] = request.POST.get('product_id')
                request.session['name'] = request.POST.get('product-title')
                request.session['img'] = request.POST.get('product-img')
                request.session['size'] = request.POST.get('product-size')
                request.session['price'] = request.POST.get('product-price')
                request.session['quantity'] = request.POST.get('product-quanity')
                total = int(request.POST.get('product-quanity')) * int(
                    request.POST.get('product-price').replace(',', ''))
                request.session['total'] = f'{total:,}'
                return redirect('/checkout.html')

            else:
                product_id = request.POST.get('product_id')
                try:
                    cart = Cart.objects.get(product=product_id)
                    update_cart_model(req=request, cart=cart, product=Products.objects.get(product_id=product_id))
                    msg = 'Cart update success!'
                except Cart.DoesNotExist:
                    product = Products.objects.get(product_id=product_id)
                    add_to_cart_model(req=request, product=product)
                    msg = 'Add to cart success!'

                messages.success(request, msg)
                return redirect('/shop.html')

    # ====== end shop-single ======

    # ====== cart ======
    if load_template == 'cart.html':
        if not request.user.is_authenticated:
            messages.info(request, 'You must login first for use this feature!')
            return redirect('login')

        cart = Cart.objects.filter(user=request.user).values('cart_id', 'product__name', 'product',
                                                             'product__price', 'product__image',
                                                             'quantity', 'price_total',
                                                             'product__size__name')

        for item in cart:
            item['price_total'] = f"{int(item['price_total']):,}"
            item['product__price'] = f"{int(item['product__price']):,}"

        context['cart_info'] = cart
        if request.POST:
            if 'delete_cart' in request.POST:
                cart_id = request.POST.get('delete_cart')
                cart = Cart.objects.get(cart_id=cart_id)
                cart.delete()
                return redirect('/cart.html')

            if 'buy' in request.POST:
                request.session['id'] = request.POST.get('product_id')
                request.session['cart_id'] = request.POST.get('cart-id')
                request.session['name'] = request.POST.get('product-title')
                request.session['img'] = request.POST.get('product-img')
                request.session['size'] = request.POST.get('product-size')
                request.session['price'] = request.POST.get('product-price')
                request.session['quantity'] = request.POST.get('product-quanity')
                request.session['total'] = request.POST.get('product-total')
                return redirect('/checkout.html')
    # ============ end cart =================

    # ====================== checkout ====================
    if load_template == 'checkout.html':
        if request.POST:
            unique_code = uuid.uuid1()

            # ---------- sandbox midtrans ----------
            transaction = get_midtrans(request, order_id=unique_code)
            # status_response = api_client.transactions.notification(mock_notification)
            # ---------- end midtrans ----------
            # ------------ save to order model ------------
            save_order = Order(
                product=Products.objects.get(product_id=request.POST.get('product-id')),
                user=request.user,
                unique_code=unique_code,
                gross_amount=int(request.POST.get('product-total').replace(',', '')),
                updated_at=datetime.now(),
                status='Pending'
            )
            save_order.save()
            # ------------ end save ------------
            # ------------ delete cart ------------
            if request.POST.get('cart-id'):
                delete_cart = Cart.objects.get(cart_id=request.POST.get('cart-id'))
                delete_cart.delete()
            # ------------ end delete cart ------------

            return redirect(transaction['redirect_url'])

            # ---- load by javascript ----------
            # request.session['transaction_token'] = transaction['token']
            # return redirect('/midtrans-test.html')

    # ====================== end checkout ====================

    if load_template == 'profile.html':

        # update status every load this page

        api_client = midtransclient.CoreApi(
            is_production=False,
            server_key='SB-Mid-server-01NTFWb6l738KBzH0OWZuhks',
            client_key='SB-Mid-client-UsEaLuaU7PMBbq_u'
        )

        unique_code = Order.objects.filter(user=request.user).values('unique_code', 'product__name')
        for item in unique_code:
            try:
                status_response = api_client.transactions.status(item['unique_code'])
                update_order = Order.objects.get(unique_code=item['unique_code'])
                update_order.status = status_response.get('transaction_status')
                update_order.save()

                obj, created = Payment.objects.update_or_create(
                    order=Order.objects.get(unique_code=item['unique_code']),
                    defaults={
                        'transaction_time': status_response.get('transaction_time'),
                        'gross_amount': int(status_response.get('gross_amount').replace('.00', '')),
                        'payment_type': status_response.get('payment_type')
                    }
                )

            except Exception as e:
                status_response = e
            # finally:
            #     context['status_code'] = status_response

    context['segment'] = load_template
    html_template = loader.get_template(load_template)
    return HttpResponse(html_template.render(context, request))


# -------------------------- function preprocessing data --------------------------

def query_get_product(param=None, field=None):
    """
    param : brand name, size name, etc
    field : field / column name
    """

    # get data from model (database)
    if param is not None and field is not None:

        if field == 'category__name':
            data_raw = Products.objects.filter(category__name=param).values('product_id', 'name', 'price', 'size__name',
                                                                            'image')
        elif field == 'brand__name':
            data_raw = Products.objects.filter(brand__name=param).values('product_id', 'name', 'price', 'size__name',
                                                                         'image')
        elif field == 'size__name':
            data_raw = Products.objects.filter(size__name=param).values('product_id', 'name', 'price', 'size__name',
                                                                        'image')
        elif field == 'size__size_category__name':
            data_raw = Products.objects.filter(size__size_category__name=param).values('product_id', 'name', 'price',
                                                                                       'size__name',
                                                                                       'image')

    elif param is not None and field is None:
        data_raw = Products.objects.filter(Q(name__icontains=param) |
                                           Q(price__icontains=param) |
                                           Q(desc__icontains=param) |
                                           Q(size__size_category__name__icontains=param)).values('name', 'product_id',
                                                                                                 'price',
                                                                                                 'size__name', 'image')

    else:
        data_raw = Products.objects.values('product_id', 'name', 'price', 'size__name', 'image')

    # preprocess data raw to clean
    list_product = defaultdict(lambda: defaultdict(list))
    for item in data_raw:
        list_product[item['name']]['product_id'].append(item['product_id'])
        list_product[item['name']]['price'].append(int(item['price']))
        list_product[item['name']]['size'].append(item['size__name'])
        list_product[item['name']]['image'].append(item['image'])

    # preprocess clean data for send to view
    output = [{'name': key, 'product_id': ' '.join(str(item) for item in value.get('product_id')),
               'price': f'{sorted(value.get("price"))[0]:,} s/d {sorted(value.get("price"))[-1]:,}' if len(
                   value.get('price')) > 1 else f'{sorted(value.get("price"))[0]:,}',
               'size': '/'.join(sorted(value.get('size'))),
               'image': value.get('image')[0]} for key, value in list_product.items()]
    return output


def details_product(param):
    raw_detail_product = Products.objects.filter(name=param).values('name', 'product_id', 'price', 'stock', 'desc',
                                                                    'size__name', 'category__name',
                                                                    'brand__name', 'image')
    # preprocess data raw to clean
    list_product = defaultdict(lambda: defaultdict(list))
    for item in raw_detail_product:
        list_product[item['name']]['price'].append(int(item['price']))
        list_product[item['name']]['product_id'].append(item['product_id'])
        list_product[item['name']]['stock'].append(item['stock'])
        list_product[item['name']]['desc'].append(item['desc'])
        list_product[item['name']]['size'].append(item['size__name'])
        list_product[item['name']]['category'].append(item['category__name'])
        list_product[item['name']]['brand'].append(item['brand__name'])
        list_product[item['name']]['image'].append(item['image'])
    return list_product


def item_shop_single(raw_detail, related_product=True):
    img = [image for key, value in raw_detail.items() for image in value.get('image')]
    context = {'available_size': [{'size': item} for key, value in raw_detail.items() for item in value.get('size')],
               'images': [img[i:i + 3] for i in range(0, len(img), 3)],
               'product_id': [item.get('product_id')[0] for item in raw_detail.values()][0],
               'brand': [item.get('brand')[0] for item in raw_detail.values()][0],
               'price': [f'{sorted(value["price"])[0]:,} s/d {sorted(value["price"])[-1]:,}'
                         if len(value['price']) > 1 else f'{sorted(value["price"])[0]:,}'
                         for key, value in raw_detail.items()][0],
               'description': [item.get('desc')[0] for item in raw_detail.values()][0],
               'available_stock': ' / '.join([f'{SIZE_DICT[size]} : {stock}' for key, value in raw_detail.items()
                                              for size, stock in zip(value.get('size'), value.get('stock'))])}

    if related_product:
        context['related_product'] = query_get_product(list(raw_detail.keys())[0].split(' ')[0])

    return context


def add_to_cart_model(req, product):
    quantity = int(req.POST.get('product-quanity')) if req.POST else 1
    Cart.objects.create(
        product=Products.objects.get(product_id=product.product_id),
        user=req.user,
        quantity=quantity,
        date=datetime.now(),
        price_total=int(product.price) * quantity
    )


def update_cart_model(req, cart, product):
    quantity = int(req.POST.get('product-quanity')) if req.POST else 1
    cart.quantity = quantity
    cart.date = datetime.now()
    cart.price_total = int(product.price) * quantity
    cart.save()


def total_product_in_cart(request):
    if request.user.is_authenticated:
        return len(Cart.objects.filter(user=request.user))
    return 0


def get_midtrans(request, order_id):
    snap = midtransclient.Snap(
        is_production=False,
        server_key='SB-Mid-server-01NTFWb6l738KBzH0OWZuhks',
        client_key='SB-Mid-client-UsEaLuaU7PMBbq_u'
    )

    param = {
        "transaction_details": {
            "order_id": f"{order_id}",
            "gross_amount": int(request.POST.get('product-total').replace(',', ''))
        }, "item_details": [{
            "id": request.POST.get('product-id'),
            "price": int(request.POST.get('product-price').replace(',', '')),
            "quantity": request.POST.get('product-qty'),
            "name": request.POST.get('product-name'),
            "brand": request.POST.get('product-price'),
            # "category": "Toys",
            # "merchant_name": "Midtrans"
        }],
        "customer_details": {
            "first_name": request.POST.get('name'),
            "email": request.POST.get('email'),
            # "phone": "+628123456",
            "billing_address": {
                "first_name": request.POST.get('name'),
                "email": request.POST.get('email'),
                # "phone": "081 2233 44-55",
                "address": request.POST.get('address'),
                "postal_code": request.POST.get('zipcode'),
                "city": request.POST.get('city'),
                "province": request.POST.get('province'),
                "country_code": "IDN"
            },
            "shipping_address": {
                "first_name": request.POST.get('name'),
                "email": request.POST.get('email'),
                # "phone": "0 8128-75 7-9338",
                "address": request.POST.get('address'),
                "postal_code": request.POST.get('zipcode'),
                "city": request.POST.get('city'),
                "province": request.POST.get('province'),
                "country_code": "IDN"
            }
        },

        "enabled_payments": ["credit_card", "mandiri_clickpay", "cimb_clicks", "bca_klikbca", "bca_klikpay",
                             "bri_epay", "echannel", "indosat_dompetku", "mandiri_ecash", "permata_va",
                             "bca_va", "gopay",
                             "bni_va", "other_va", "kioson", "indomaret", "gci", "danamon_online"],
        # "gopay_partner": {
        #     "phone_number": "81234567891",
        #     "country_code": "62",
        #     "redirect_url": "https://mywebstore.com/gopay-linking-finish"  # please update with your redirect URL
        # },
        "bca_va": {
            "va_number": "12345678911",
            "free_text": {
                "inquiry": [
                    {
                        "en": "text in English",
                        "id": "text in Bahasa Indonesia"
                    }
                ],
                "payment": [
                    {
                        "en": "text in English",
                        "id": "text in Bahasa Indonesia"
                    }
                ]
            }
        },
        "bni_va": {
            "va_number": "12345678"
        },
        "permata_va": {
            "va_number": "1234567890",
            "recipient_name": "SUDARSONO"
        },
        "callbacks": {
            "finish": "http://192.168.0.103:8001/"
        },
        "expiry": {
            "start_time": str(datetime.now().replace(microsecond=0)) + "+0700",
            "unit": "minute",
            "duration": 60 * 24
        },
    }
    # create transaction
    transaction = snap.create_transaction(param)
    return transaction

# -------------------------- end function preprocessing data --------------------------
