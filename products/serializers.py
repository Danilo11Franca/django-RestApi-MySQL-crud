from rest_framework import serializers 
from products.models import Product, ProductAttribute, ProductBarcode
 
 
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'sku', 'description', 'price', 'created', 'last_updated')

class ProductBarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBarcode
        fields = ('product', 'barcode')

class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ('product', 'name', 'value')