from datetime import datetime
from django.shortcuts import render

from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser 
from rest_framework import status
 
from products.models import Product, ProductAttribute, ProductBarcode
from products.serializers import ProductAttributeSerializer, ProductBarcodeSerializer, ProductSerializer
from rest_framework.decorators import api_view

from copy import deepcopy

@api_view(['GET', 'POST'])
def product_list(request):

    #GET /api/products
    if request.method == 'GET':
        success_return = {
            "totalCount": 0,
            "items": []
        }

        #obtém produtos do banco de dados
        products = Product.objects.all()

        #verifica se request tem o parâmetro "start"
        start = request.GET.get('start', 0)
        if start is not 0:
            #se sim, obtém os produtos com id maior ou igual ao valor do parâmetro
            products = products.filter(id__gte=start)

        #verifica se request tem o parâmetro "sku"
        sku = request.GET.get('sku', None)
        if sku is not None:
            #se sim, obtém os produtos que possuem como substring o "sku" especificado
            products = products.filter(sku__icontains=sku)

        products = products.values()

        #verifica se request tem o parâmetro "num", por padrão esse valor é 10
        num = request.GET.get('num', 10)

        #diminui a lista de produtos para o num especificado    
        products = products[:int(num)]

        #lista de dicionários
        products = list(products)

        #obtém códigos de barras e atributos do banco de dados
        product_barcodes = ProductBarcode.objects.all()
        product_attributes = ProductAttribute.objects.all()

        #faz um "JOIN" entre produtos, códigos de barras e atributos pelo id
        for i in range(len(products)):
            (products[i])["barcodes"] = []
            for bc in list((product_barcodes.filter(product_id=(products[i])["id"])).values('barcode')):
                (products[i])["barcodes"] = (products[i])["barcodes"] + [bc["barcode"]]

            (products[i])["attributes"] = list((product_attributes.filter(product_id=(products[i])["id"])).values('name', 'value'))

        #verifica se request tem o parâmetro "barcode"
        barcode = request.GET.get('barcode', None)

        products_filter = deepcopy(products)
        
        if barcode is not None:
            #se sim, filtra os objetos pelos códigos de barras que têm como substring o barcode especificado
            for i in range(len(products)):
                if len((products[i])["barcodes"]) == 0:
                    products_filter.remove(products[i])
                else:
                    for bc in (products[i])["barcodes"]:
                        if barcode not in bc:
                            products_filter.remove(products[i])
        
        products = deepcopy(products_filter)

        #verifica se request tem o parâmetro "fields"
        fields = request.GET.get('fields', None)

        if fields is not None:
            #se sim, identifica quais são os campos especificados
            fields = fields.split(',')
            fields = set(fields)
            fields_filter = {"id", "title", "sku", "description", "price",  "created", "last_updated", "barcodes", "attributes"}
            fields_filter = fields_filter.difference(fields)
            #elimina os campos especificados
            for i in range(len(products)):
                for field in fields_filter:
                    (products[i]).pop(field, None)
        
        success_return["totalCount"] = len(products)
        success_return["items"] = products
        
        #products_serializer = ProductSerializer(products, many=True)
        return JsonResponse(success_return, safe=False)
        # 'safe=False' for objects serialization
    
    #POST /api/products
    elif request.method == 'POST':
        #produto a ser inserido
        product_data = JSONParser().parse(request)

        #produto sem código de barras e atributos
        product = {}
        #product receberá todos os valores de product_data,
        #com exceção dos valores correspondentes ao código de barras e atributos, se existirem
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
                #se valor de barcode foi especificado, verifica se o(s) valor(es) já existem no banco de dados
                if len(product_data["barcodes"]) > 0:   
                    for barcode in product_data["barcodes"]:
                        for bc in list(ProductBarcode.objects.values('barcode')):
                            if barcode == bc["barcode"]:
                                #se sim, retorna erro
                                return JsonResponse({"errorText": "barcode '{}' already exists".format(barcode)}, status=status.HTTP_400_BAD_REQUEST)
            
            #se valor de barcode não existe no banco de dados ou não foi especificado,
            #insere produto
            product_serializer.save()

            #insere código de barras, caso tenha sido especificado
            if "barcodes" in product_data:
                if len(product_data["barcodes"]) > 0:
                    for barcode in product_data["barcodes"]:
                        product_barcode_serializer = ProductBarcodeSerializer(data={"product": product_serializer.data["id"], "barcode": barcode})
                        if product_barcode_serializer.is_valid():
                            product_barcode_serializer.save()
                        else:
                            return JsonResponse(product_barcode_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            #insere atributo, caso tenha sido especificado
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
 
 
@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    #obtém produto com o id especificado
    product = Product.objects.all().filter(pk=pk).values()

    #lista com um ou nenhum produto
    product = list(product)

    if len(product) == 0:
        #se não existe produto correspondente, retorna erro
        return JsonResponse({"errorText": "Can’t find product ({})".format(pk)}, status=status.HTTP_404_NOT_FOUND)
    
    #dicionário
    product = product[0]
 
    #GET /api/products/{id}
    if request.method == 'GET':
        #obtém código de barras e atributos que tenham o id especificado
        product_barcodes = ProductBarcode.objects.all().filter(product_id=pk).values('barcode')
        product_attributes = ProductAttribute.objects.all().filter(product_id=pk).values('name', 'value')

        #insere novo campo "barcodes" em product
        product["barcodes"] = []

        #adiciona códigos de barras obtidos ao novo campo de product
        for barcode in list(product_barcodes):
            product["barcodes"] = product["barcodes"] + [barcode["barcode"]]

        #insere novo campo "attributes" em product e adiciona atributos obtidos ao novo campo
        product["attributes"] = list(product_attributes)

        #product_serializer = ProductSerializer(product) 
        return JsonResponse(product, safe=False)
 
    #PUT /api/products/{id}
    elif request.method == 'PUT':
        #produto do banco de dados a ser atualizado
        product = Product.objects.get(pk=pk)

        #produto com as novas informações
        product_data = JSONParser().parse(request)

        #produto sem código de barras e atributos
        product_update = {}
        #product_update receberá todos os valores de product_data,
        #com exceção dos valores correspondentes ao código de barras e atributos, se existirem
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
        
        #atualiza data de atualização
        product_update["last_updated"] = datetime.now()

        product_serializer = ProductSerializer(product, data=product_update) 
        if product_serializer.is_valid():
            #atualiza produto com as novas alterações
            product_serializer.save()

            if "barcodes" in product_data:
                #se valor de barcode foi especificado, e se esse valor não existe no banco de dados,
                #insere código de barras
                if len(product_data["barcodes"]) > 0:
                    for barcode in product_data["barcodes"]:
                        if not(barcode in list(ProductBarcode.objects.values('product_id', 'barcode'))):
                            product_barcode_serializer = ProductBarcodeSerializer(data={"product": pk, "barcode": barcode})
                            if product_barcode_serializer.is_valid():
                                product_barcode_serializer.save()
            
            if "attributes" in product_data:
                #se valor de attributes foi especificado,
                #e se esse valor não existe nos atributos do objeto que foi inserido, insere atributos
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

    #DELETE /api/products/{id}
    elif request.method == 'DELETE':
        #obtém produto a ser excluido e remove do banco de dados
        product = Product.objects.get(pk=pk)
        product.delete()
        return JsonResponse(True, status=status.HTTP_204_NO_CONTENT, safe=False)