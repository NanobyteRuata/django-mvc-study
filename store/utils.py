from .models import *
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    print('Cart: ', cart)

    items = []
    order = {
        'getCartTotal': 0,
        'getCartItems': 0
    }
    cartItems = order['getCartItems']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']
            product = Product.objects.get(id=i)
            total = product.price * cart[i]['quantity']

            order['getCartTotal'] += total
            order['getCartItems'] += cart[i]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageUrl': product.imageUrl
                },
                'quantity': cart[i]['quantity'],
                'getTotal': total
            }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    return {'cartItems':cartItems, 'order':order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete="incomplete")
        items = order.orderitem_set.all()
        cartItems = order.getCartItems
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'cartItems':cartItems, 'order':order, 'items': items}


def guestOrder(request, data):
    print('User is not logged in')

    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email=email,
    )
    customer.name = data['form']['name']
    customer.phone = data['form']['phone']
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete="incomplete",
    )

    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )
    return customer, order

def makePagination(request, model, type, order):
    objects_list = model.objects.all().order_by(order)
    paginator = Paginator(objects_list, 20)
    page = request.GET.get(type)

    try:
        to_show = paginator.page(page)
    except PageNotAnInteger:
        to_show = paginator.page(1)
    except EmptyPage:
        to_show = paginator.page(paginator.num_pages)

    return to_show, paginator
