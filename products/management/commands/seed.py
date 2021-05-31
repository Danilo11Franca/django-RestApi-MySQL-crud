#products/management/commands/seed.py
from products.factory import ProductFactory
from django.core.management.base import BaseCommand

# import UserFactory here


class Command(BaseCommand):
    help = 'Seeds the database.'

    def add_arguments(self, parser):
        parser.add_argument('--products',
            default=10,
            type=int,
            help='The number of fake products to create.')

    def handle(self, *args, **options):
        for _ in range(options['products']):
            ProductFactory.create()