from django.db import models
from products.models import Product


class Sale(models.Model):
    datetime_created = models.DateTimeField(auto_now=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.IntegerField(default=1)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"SALE: [{self.product.name}] | PRICE: [{self.selling_price}]"


class Purchase(models.Model):
    datetime_created = models.DateTimeField(auto_now=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.IntegerField(default=1)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"SALE: [{self.product.name}] | PRICE: [{self.purchase_price}]"
