from datetime import datetime
from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=32)
    sku = models.CharField(max_length=32, unique=True, default='')
    description = models.CharField(max_length=1024, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created = models.DateTimeField(default=datetime.now())
    last_updated = models.DateTimeField(null=True)
    
    class Meta:  
        db_table = "product"
    
    def __str__(self):
        return self

class ProductBarcode(models.Model):
    product = models.ForeignKey('Product',on_delete=models.CASCADE)
    barcode = models.CharField(max_length=32, unique=True)
    
    class Meta:  
        db_table = "product_barcode"
    
    def __str__(self):
        return self

class ProductAttribute(models.Model):
    product = models.ForeignKey('Product',on_delete=models.CASCADE)
    name = models.CharField(max_length=16)
    value = models.CharField(max_length=32)
    
    class Meta:  
        db_table = "product_attribute"
    
    def __str__(self):
        return self
