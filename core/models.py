from django.conf import settings
from django.db import models

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
    #TO-DO: Erase the nullable feature at the end
    category = models.ForeignKey(CategoryChoices, on_delete=models.CASCADE, null=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)

    def __str__(self):
        return self.title

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
