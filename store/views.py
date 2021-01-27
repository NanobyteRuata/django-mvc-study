from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cartData, guestOrder, makePagination
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage


# Create your views here.
def store(request):
    is_storeadmin = False
    if request.user.groups.filter(name='storeadmins').exists():
        is_storeadmin = True
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems, 'shipping': False, 'is_storeadmin': is_storeadmin}
    return render(request, 'store/store.html', context)


def cart(request):
    is_storeadmin = False
    if request.user.groups.filter(name='storeadmins').exists():
        is_storeadmin = True

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'shipping': False,
               'is_storeadmin': is_storeadmin}
    return render(request, 'store/cart.html', context)


def checkout(request):
    is_storeadmin = False
    if request.user.groups.filter(name='storeadmins').exists():
        is_storeadmin = True

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'shipping': False,
               'is_storeadmin': is_storeadmin}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    product = Product.objects.get(id=productId)

    if action == 'update_add' or action == 'update_remove':
        print(data['orderId'])
        orderId = data['orderId']
        order = Order.objects.get(id=orderId)
    else:
        order, created = Order.objects.get_or_create(customer=customer, complete="incomplete")

    orderitem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add' or action == 'update_add':
        orderitem.quantity = (orderitem.quantity + 1)
    elif action == 'remove' or action == 'update_remove':
        orderitem.quantity = (orderitem.quantity - 1)

    orderitem.save();
    if (orderitem.quantity <= 0):
        orderitem.delete()

    print('productId: ', productId)
    print('action: ', action)
    return JsonResponse('item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete="incomplete")

    else:
        customer, order = guestOrder(request, data)

    total = int(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.getCartTotal:
        order.complete = "completed"

    order.save()

    if order.shipping == True:
        DeliveryAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            street=data['shipping']['street'],
            township=data['shipping']['township'],
            city=data['shipping']['city'],
        )

    return JsonResponse('payment complete', safe=False)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user != None:
            login(request, user)
            return redirect('store')
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {}
    return render(request, 'store/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('store');


def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            Customer.objects.create(
                name=username,
                user=User.objects.get(email=email),
                phone=request.POST.get('phone'),
                email=email,
            )
            messages.success(request, 'Account was created for ' + username)
            return redirect('login')

    context = {'form': form}
    return render(request, 'store/register.html', context)


def dashboardPage(request):
    if not request.user.groups.filter(name='storeadmins').exists():
        messages.warning(request, 'Only store admins are authorized for the dashboard.')
        return redirect('login')

    pagetype = 'orders'
    if request.GET.get('type') == 'orders' or \
            request.GET.get('type') == 'products' or \
            request.GET.get('type') == 'customers':
        pagetype = request.GET.get('type')

    data = cartData(request)
    cartItems = data['cartItems']

    context = {'cartItems': cartItems,
               'is_storeadmin': True,
               'type': pagetype}

    if pagetype == 'orders':
        paginated_orders, orders_paginator = makePagination(request, Order, 'orders_page', 'date_order')
        orders_to_show = []
        for order in paginated_orders:
            orders_to_show.append({
                'id': order.id,
                'customer_name': Customer.objects.get(name=order.customer.name),
                'items_count': len(OrderItem.objects.filter(order=order)),
                'status': order.complete,
                'date_order': order.date_order
            })
        context.update({'orders': orders_to_show,
                        'paginated_orders': paginated_orders,
                        'orders_paginator': orders_paginator})

    if pagetype == 'products':
        products_to_show, products_paginator = makePagination(request, Product, 'products_page', 'name')
        context.update({'products': products_to_show,
                        'products_paginator': products_paginator})

    if pagetype == 'customers':
        customers_to_show, customers_paginator = makePagination(request, Customer, 'customers_page', 'id')
        context.update({'customers': customers_to_show,
                        'customers_paginator': customers_paginator})

    return render(request, 'store/dashboard.html', context)

def detailPage(request):
    if not request.user.groups.filter(name='storeadmins').exists():
        messages.warning(request, 'Only store admins are authorized for the dashboard.')
        return redirect('login')

    item_id = request.GET.get('id')
    pagetype = 'orders'
    if request.GET.get('type') == 'orders' or \
            request.GET.get('type') == 'products' or \
            request.GET.get('type') == 'customers':
        pagetype = request.GET.get('type')

    data = cartData(request)
    cartItems = data['cartItems']

    if request.method == 'POST':
        if pagetype == 'customers':
            update_customer = Customer.objects.get(id=request.GET.get('id'))
            update_customer.name = request.POST.get('name')
            update_customer.phone = request.POST.get('phone')
            update_customer.email = request.POST.get('email')
            update_customer.save()
        if pagetype == 'products':
            update_products = Product.objects.get(id=request.GET.get('id'))
            if request.FILES['image']:
                myfile = request.FILES['image']
                fs = FileSystemStorage()
                fs.save(myfile.name, myfile)
                update_products.image = myfile
            update_products.name = request.POST.get('name')
            update_products.price = request.POST.get('price')
            update_products.save()
        if pagetype == 'orders':
            update_orders = Order.objects.get(id=request.GET.get('id'))
            update_orders.complete = request.POST.get('options')
            update_orders.save()
            address = DeliveryAddress.objects.get(order=update_orders)
            address.address = request.POST.get('address')
            address.street = request.POST.get('street')
            address.township = request.POST.get('township')
            address.city = request.POST.get('city')
            address.save()
        return redirect('dashboard')

    context = {
        'cartItems': cartItems,
        'is_storeadmin': True,
        'type': pagetype,
    }

    if pagetype == 'orders':
        order = Order.objects.get(id=item_id)
        orderitems = OrderItem.objects.filter(order=order)
        item = {
            'customer': Customer.objects.get(id=order.customer.id),
            'order': order,
            'address': DeliveryAddress.objects.get(order=order),
            'orderitems': orderitems,
            'status': ('completed', 'confirmed', 'delivered',),
        }
        context.update({'item': item})
    elif pagetype == 'products':
        product = Product.objects.get(id=item_id)
        item = {
            'product': product,
        }
        if request.GET.get('action') == 'create':
            item.update({'action': 'create'})
        else:
            item.update({'action': 'update'})
        context.update({'item': item})
    elif pagetype == 'customers':
        customer = Customer.objects.get(id=item_id)
        item = {
            'customer': customer,
        }
        item.update({'action': 'update'})
        context.update({'item': item})

    return render(request, 'store/detail.html', context)
