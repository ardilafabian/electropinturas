from django.contrib import admin

from .models import Item, OrderItem, Order, CategoryChoices, BillingAddress, Coupon, Refund

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)

make_refund_accepted.short_description = "Update orders to refund granted"

class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted',
        'billing_address',
        'coupon'
    ]
    list_display_links = [
        'user',
        'billing_address',
        'coupon'
    ]
    list_filter = [
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted'
    ]
    search_fields = [
        'user__username',
        'ref_code'
    ]

    actions = [make_refund_accepted]

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(CategoryChoices)
admin.site.register(BillingAddress)
admin.site.register(Coupon)
