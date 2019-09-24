from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .forms import CheckoutForm, CouponForm
from .models import Item, OrderItem, Order, BillingAddress, Coupon


def products(request):
    context = {
        'items' : Item.objects.all()
    }
    return render(request, "products.html", context)

class CheckoutView(View):
    def get(self, *args, **kwargs):
        # Form
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form':form,
            'couponform':CouponForm(),
            'order':order,
            'DISPLAY_COUPON_FORM':True
        }
        return render(self.request, "checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            #print(self.request.POST)
            if form.is_valid():
                #print(form.cleaned_data)
                #print("The form is valid.")

                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: Add functionality for these fields
                #same_shipping_address = form.cleaned_data.get('same_shipping_address')
                #save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )

                billing_address.save()
                order.billing_address = billing_address
                order.save()

                # TODO: Add redirect to cash payment
                if payment_option == 'S':
                    return redirect("core:payment", payment_option='stripe')
                elif payment_option == 'P':
                    return redirect("core:payment", payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option selected.")
                    return redirect("core:checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "Tu no tienes una orden activa.")
            return redirect("core:order-summary")

class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, "payment.html")

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home.html"

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object':order,
            }
            return render(self.request, "order_summary.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "Tu no tienes una orden activa.")
            return redirect("/")

class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

@login_required
def add_to_cart(request, slug):
     item = get_object_or_404(Item, slug=slug)
     order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
     )
     order_qs = Order.objects.filter(user=request.user, ordered=False)
     if order_qs.exists():
         order = order_qs[0]
         # Check if the order item is in the order
         if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "La cantidad de este producto fue actualizada.")
            return redirect("core:order-summary")
         else:
            messages.info(request, "Este producto fue añadido a tu pedido.")
            order.items.add(order_item)
            return redirect("core:order-summary")
     else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Este producto fue añadido a tu pedido.")
     return redirect("core:order-summary")

@login_required
def remove_from_cart(request, slug):
     item = get_object_or_404(Item, slug=slug)
     order_qs = Order.objects.filter(
         user=request.user,
         ordered=False,
     )
     if order_qs.exists():
         order = order_qs[0]
         # Check if the order item is in the order
         if order.items.filter(item__slug=item.slug).exists():
             order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
             )[0]
             order.items.remove(order_item)
             messages.info(request, "Este producto fue eliminado de tu pedido.")
             return redirect("core:order-summary")
         else:
             messages.info(request, "Este producto no se encuentra en tu pedido.")
             return redirect("core:product", slug=slug)
     else:
         messages.info(request, "Tu no tienes una orden activa.")
         return redirect("core:product", slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
     item = get_object_or_404(Item, slug=slug)
     order_qs = Order.objects.filter(
         user=request.user,
         ordered=False,
     )
     if order_qs.exists():
         order = order_qs[0]
         # Check if the order item is in the order
         if order.items.filter(item__slug=item.slug).exists():
             order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
             )[0]
             if order_item.quantity > 1:
                 order_item.quantity -= 1
                 order_item.save()
             else:
                 order.items.remove(order_item)
             messages.info(request, "La cantidad de este producto fue actualizada.")
             return redirect("core:order-summary")
         else:
             messages.info(request, "Este producto no se encuentra en tu pedido.")
             return redirect("core:product", slug=slug)
     else:
         messages.info(request, "Tu no tienes una orden activa.")
         return redirect("core:product", slug=slug)

def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist as e:
        messages.info(request, "Este cupón no existe.")
        return redirect("core:checkout")

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')

                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)

                order.save()

                messages.success(self.request, "Cupón agregado exitósamente")
                return redirect("core:checkout")
            except ObjectDoesNotExist as e:
                messages.info(self.request, "Tu no tienes una orden activa.")
                return redirect("core:checkout")
