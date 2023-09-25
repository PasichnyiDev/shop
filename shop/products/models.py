from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"CATEGORY: [{self.name}]"


class Product(models.Model):
    article = models.CharField(max_length=50, blank=True, null=True)
    name = models.TextField()
    brand = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock_amount = models.IntegerField(default=0)
    category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"PRODUCT: [{self.name}]"
