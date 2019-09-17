from django.conf import settings
from django.db import models
from django.shortcuts import reverse

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

class CategoryChoices(models.Model):
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.title

class Item(models.Model):
    code = models.CharField(max_length=20, default='0000')
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    #TO-DO: Erase the nullable feature at the end
    category = models.ForeignKey(CategoryChoices, on_delete=models.CASCADE, null=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    #Moment that that the order is created
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False )

    def __str__(self):
        return self.user.username
