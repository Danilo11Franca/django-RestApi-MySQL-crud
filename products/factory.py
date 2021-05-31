from products.models import Product
import factory  
import factory.django

class ProductFactory(factory.django.DjangoModelFactory):  
    class Meta:
        model = Product

    title = factory.Faker('text')
    sku = factory.Faker('text')
    description = factory.Faker('text')