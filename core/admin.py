from django.contrib import admin

from .models import Item, OrderItem, Order, CategoryChoices, BillingAddress, Coupon

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', ]

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(CategoryChoices)
admin.site.register(BillingAddress)
admin.site.register(Coupon)
