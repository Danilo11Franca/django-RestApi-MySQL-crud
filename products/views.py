from datetime import datetime
from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
 
from products.models import Product, ProductAttribute, ProductBarcode
from products.serializers import ProductAttributeSerializer, ProductBarcodeSerializer, ProductSerializer
from rest_framework.decorators import api_view

from copy import deepcopy

@api_view(['GET', 'POST', 'DELETE'])
def product_list(request):

    if request.method == 'GET':
        success_return = {
            "totalCount": 0,
            "items": []
        }

        products = Product.objects.all()

        start = request.GET.get('start', 0)
        if start is not 0:
            products = products.filter(id__gte=start)

        sku = request.GET.get('sku', None)
        if sku is not None:
            products = products.filter(sku__icontains=sku)

        products = products.values()

        num = request.GET.get('num', 10)
            
        products = products[:int(num)]

        products = list(products)

        product_barcodes = ProductBarcode.objects.all()
        product_attributes = ProductAttribute.objects.all()

        for i in range(len(products)):
            (products[i])["barcodes"] = []
            for bc in list((product_barcodes.filter(product_id=(products[i])["id"])).values('barcode')):
                (products[i])["barcodes"] = (products[i])["barcodes"] + [bc["barcode"]]

            (products[i])["attributes"] = list((product_attributes.filter(product_id=(products[i])["id"])).values('name', 'value'))

        barcode = request.GET.get('barcode', None)

        products_filter = deepcopy(products)
        
        if barcode is not None:
            for i in range(len(products)):
                if len((products[i])["barcodes"]) == 0:
                    products_filter.remove(products[i])
                else:
                    for bc in (products[i])["barcodes"]:
                        if barcode not in bc:
                            products_filter.remove(products[i])
        
        products = deepcopy(products_filter)

        fields = request.GET.get('fields', None)
        if fields is not None:
            fields = fields.split(',')
            fields = set(fields)
            fields_filter = {"id", "title", "sku", "description", "price",  "created", "last_updated", "barcodes", "attributes"}
            fields_filter = fields_filter.difference(fields)
            for i in range(len(products)):
                for field in fields_filter:
                    (products[i]).pop(field, None)
        
        success_return["totalCount"] = len(products)
        success_return["items"] = products
        
        #products_serializer = ProductSerializer(products, many=True)
        return JsonResponse(success_return, safe=False)
        # 'safe=False' for objects serialization
 
    elif request.method == 'POST':
        product_data = JSONParser().parse(request)

        product = {}
        if "title" in product_data:
            product["title"] = product_data["title"]
        else:
            return JsonResponse({"errorText": "field 'title' required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if "sku" in product_data:
            product["sku"] = product_data["sku"]
        else:
            return JsonResponse({"errorText": "field 'sku' required"}, status=status.HTTP_400_BAD_REQUEST)

        if "description" in product_data:
            product["description"] = product_data["description"]

        if "price" in product_data:
            product["price"] = product_data["price"]

        product_serializer = ProductSerializer(data=product)
        if product_serializer.is_valid():
            
            if "barcodes" in product_data:
                if len(product_data["barcodes"]) > 0:   
                    for barcode in product_data["barcodes"]:
                        for bc in list(ProductBarcode.objects.values('barcode')):
                            if barcode == bc["barcode"]:
                                return JsonResponse({"errorText": "barcode '{}' already exists".format(barcode)}, status=status.HTTP_400_BAD_REQUEST)
            
            product_serializer.save()

            if "barcodes" in product_data:
                if len(product_data["barcodes"]) > 0:
                    for barcode in product_data["barcodes"]:
                        product_barcode_serializer = ProductBarcodeSerializer(data={"product": product_serializer.data["id"], "barcode": barcode})
                        if product_barcode_serializer.is_valid():
                            product_barcode_serializer.save()
                        else:
                            return JsonResponse(product_barcode_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            if "attributes" in product_data:
                if len(product_data["attributes"]) > 0:                
                    for attribute in product_data["attributes"]:
                        product_attribute_serializer = ProductAttributeSerializer(data={"product": product_serializer.data["id"], 
                                                                                        "name": attribute["name"],
                                                                                        "value": attribute["value"]})
                        if product_attribute_serializer.is_valid():
                            product_attribute_serializer.save()
                        else:
                            return JsonResponse(product_attribute_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse(product_serializer.data["id"], status=status.HTTP_201_CREATED, safe=False)

        return JsonResponse({"errorText": "SKU '{}' already exists".format(product_data["sku"])}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        count = Product.objects.all().delete()
        return JsonResponse({"message": '{} Products were deleted successfully!'.format(count[0])}, status=status.HTTP_204_NO_CONTENT)
 
 
@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    product = Product.objects.all().filter(pk=pk).values()
    product = list(product)
    if len(product) == 0:
        return JsonResponse({"errorText": "Can’t find product ({})".format(pk)}, status=status.HTTP_404_NOT_FOUND)
    product = product[0]
 
    if request.method == 'GET':
        product_barcodes = ProductBarcode.objects.all().filter(product_id=pk).values('barcode')
        product_attributes = ProductAttribute.objects.all().filter(product_id=pk).values('name', 'value')

        product["barcodes"] = []

        for barcode in list(product_barcodes):
            product["barcodes"] = product["barcodes"] + [barcode["barcode"]]

        product["attributes"] = list(product_attributes)

        #product_serializer = ProductSerializer(product) 
        return JsonResponse(product, safe=False)
 
    elif request.method == 'PUT':
        product = Product.objects.get(pk=pk)
        product_data = JSONParser().parse(request)

        product_update = {}

        if "title" in product_data:
            product_update["title"] = product_data["title"]
        
        if "sku" in product_data:
            if product_data != None:
                product_update["sku"] = product_data["sku"]
            else:
                return JsonResponse({"errorText": "invalid sku, can not be null"}, status=status.HTTP_400_BAD_REQUEST)

        if "description" in product_data:
            product_update["description"] = product_data["description"]

        if "price" in product_data:
            product_update["price"] = product_data["price"]
        
        product_update["last_updated"] = datetime.now()

        product_serializer = ProductSerializer(product, data=product_update) 
        if product_serializer.is_valid():
            product_serializer.save()

            if "barcodes" in product_data:
                if len(product_data["barcodes"]) > 0:
                    for barcode in product_data["barcodes"]:
                        if not(barcode in list(ProductBarcode.objects.values('product_id', 'barcode'))):
                            product_barcode_serializer = ProductBarcodeSerializer(data={"product": pk, "barcode": barcode})
                            if product_barcode_serializer.is_valid():
                                product_barcode_serializer.save()
            
            if "attributes" in product_data:
                if len(product_data["attributes"]) > 0:                
                    for attribute in product_data["attributes"]:
                        for att in list(ProductAttribute.objects.values('product_id', 'name')):
                            if attribute["name"] != att["name"] and pk == att["product_id"]:
                                product_attribute_serializer = ProductAttributeSerializer(data={"product": pk, 
                                                                                                "name": attribute["name"],
                                                                                                "value": attribute["value"]})
                                if product_attribute_serializer.is_valid():
                                    product_attribute_serializer.save()
                                else:
                                    return JsonResponse(product_attribute_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse(True, status=status.HTTP_201_CREATED, safe=False)
        return JsonResponse(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
 
    elif request.method == 'DELETE':
        product = Product.objects.get(pk=pk)
        product.delete()
        return JsonResponse(True, status=status.HTTP_204_NO_CONTENT, safe=False)
    
        
@api_view(['GET'])
def product_list_published(request):
    products = Product.objects.filter(published=True)
        
    if request.method == 'GET': 
        products_serializer = ProductSerializer(products, many=True)
        return JsonResponse(products_serializer.data, safe=False)
    
