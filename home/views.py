from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import *
from django.db.models import Q
from django.shortcuts import redirect
from collections import defaultdict

# Create your views here.
SIZE_DICT = {'S': 'Small', 'L': 'Large', 'XL': 'Extra Large', 'XXL': 'Extra Extra Large'}


def index(request):
    context = {}
    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


def pages(request):
    context = {}

    load_template = request.path.split('/')[-1]
    # MENU ADMIN
    if load_template == 'admin':
        return HttpResponseRedirect(reverse('admin:index'))

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

        # return redirect('/about.html')

    # ====== END SHOP MENU ======

    # ====== PRODUCT DETAIL ======
    if load_template == 'shop-single.html':

        if request.GET.get('name'):

            # General shop-single
            name_product = request.GET.get('name')
            context['name'] = name_product

            raw_detail = details_product(name_product)
            context.update(item_details_product(raw_detail))


            # End general shop-single

            if request.GET.get('size'):
                for key, value in raw_detail.items():
                    if request.GET.get('size') in value.get('size'):
                        i = value.get('size').index(request.GET.get('size'))    # index of size
                        raw_detail_filter_size = {key: {key: [value[i]] for key, value in value.items()}}
                        context.update(item_details_product(raw_detail_filter_size))

    # ====== END PRODUCT DETAIL ======

    context['segment'] = load_template
    html_template = loader.get_template(load_template)
    return HttpResponse(html_template.render(context, request))


# -------------------------- function preprocessing data --------------------------

def query_get_product(param=None, field=None):
    # get data from model (database)
    if param is not None and field is not None:

        if field == 'category__name':
            data_raw = Products.objects.filter(category__name=param).values('name', 'price', 'size__name', 'image')
        elif field == 'brand__name':
            data_raw = Products.objects.filter(brand__name=param).values('name', 'price', 'size__name', 'image')
        elif field == 'size__name':
            data_raw = Products.objects.filter(size__name=param).values('name', 'price', 'size__name', 'image')
        elif field == 'size__size_category__name':
            data_raw = Products.objects.filter(size__size_category__name=param).values('name', 'price', 'size__name',
                                                                                       'image')

    elif param is not None and field is None:
        data_raw = Products.objects.filter(Q(name__icontains=param) |
                                           Q(price__icontains=param) |
                                           Q(desc__icontains=param) |
                                           Q(size__size_category__name__icontains=param)).values('name', 'price',
                                                                                                 'size__name', 'image')

    else:
        data_raw = Products.objects.values('name', 'price', 'size__name', 'image')

    # preprocess data raw to clean
    list_product = defaultdict(lambda: defaultdict(list))
    for item in data_raw:
        list_product[item['name']]['price'].append(int(item['price']))
        list_product[item['name']]['size'].append(item['size__name'])
        list_product[item['name']]['image'].append(item['image'])

    # preprocess clean data for send to view
    output = [{'name': key,
               'price': f'{sorted(value.get("price"))[0]:,} s/d {sorted(value.get("price"))[-1]:,}' if len(
                   value.get('price')) > 1 else f'{sorted(value.get("price"))[0]:,}',
               'size': '/'.join(sorted(value.get('size'))),
               'image': value.get('image')[0]} for key, value in list_product.items()]
    return output


def details_product(param):
    raw_detail_product = Products.objects.filter(name=param).values('name', 'price', 'stock', 'desc',
                                                                    'size__name', 'category__name',
                                                                    'brand__name', 'image')
    # preprocess data raw to clean
    list_product = defaultdict(lambda: defaultdict(list))
    for item in raw_detail_product:
        list_product[item['name']]['price'].append(int(item['price']))
        list_product[item['name']]['stock'].append(item['stock'])
        list_product[item['name']]['desc'].append(item['desc'])
        list_product[item['name']]['size'].append(item['size__name'])
        list_product[item['name']]['category'].append(item['category__name'])
        list_product[item['name']]['brand'].append(item['brand__name'])
        list_product[item['name']]['image'].append(item['image'])
    return list_product


def item_details_product(raw_detail):
    img = [image for key, value in raw_detail.items() for image in value.get('image')]
    context = {'available_size': [{'size': item} for key, value in raw_detail.items() for item in value.get('size')],
               'images': [img[i:i+3] for i in range(0, len(img), 3)],
               'brand': [item.get('brand')[0] for item in raw_detail.values()][0],
               'price': [f'{sorted(value["price"])[0]:,} s/d {sorted(value["price"])[-1]:,}'
                         if len(value['price']) > 1 else f'{sorted(value["price"])[0]:,}'
                         for key, value in raw_detail.items()][0],
               'description': [item.get('desc')[0] for item in raw_detail.values()][0],
               'available_stock': ' / '.join([f'{SIZE_DICT[size]} : {stock}' for key, value in raw_detail.items()
                                              for size, stock in zip(value.get('size'), value.get('stock'))]),
               'related_product': query_get_product(list(raw_detail.keys())[0].split(' ')[0])}
    return context

# -------------------------- end function preprocessing data --------------------------
