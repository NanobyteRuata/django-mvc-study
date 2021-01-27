from django.contrib import admin
from .models import *

class CustomizedOrder(admin.ModelAdmin):
    search_fields = ('transaction_id', 'complete',)
    list_display = ('customer_id', 'id', 'complete', 'date_order')
    list_filter = ('date_order', 'complete')

class CustomizedDelivery(admin.ModelAdmin):
    list_display = ('customer_id', 'township', 'city')
    list_filter = ('township',)

class CustomizedCustomer(admin.ModelAdmin):
    search_fields = ('name', 'email')
    list_display = ('name', 'id', 'user', 'phone', 'email')

class CustomizedOrderItem(admin.ModelAdmin):
    search_fields = ('product',)
    list_display = ('order', 'product', 'quantity',)
    list_filter = ('order',)


# Register your models here.
admin.site.register(Customer, CustomizedCustomer)
admin.site.register(Product)
admin.site.register(Order, CustomizedOrder)
admin.site.register(OrderItem, CustomizedOrderItem)
admin.site.register(DeliveryAddress, CustomizedDelivery)
