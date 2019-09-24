from django.contrib import admin

from .models import Item, OrderItem, Order, CategoryChoices, BillingAddress

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(CategoryChoices)
admin.site.register(BillingAddress)
