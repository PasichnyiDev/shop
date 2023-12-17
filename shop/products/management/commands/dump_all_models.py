import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps


class Command(BaseCommand):
    dump_models = {
        'products.ProductCategory': 'product_categories.json',
        'products.Product': 'products.json',
        'transactions.Sale': 'sales.json',
        'transactions.Purchase': 'purchases.json'
    }

    def handle(self, *args, **options):
        output_dir = 'data_dumps'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for model_name, file_name in self.dump_models.items():
            file_path = os.path.join(output_dir, file_name)
            try:
                model = apps.get_model(model_name)
                with open(file_path, 'w') as f:
                    call_command('dumpdata', model_name, stdout=f)
                self.stdout.write(self.style.SUCCESS(f'Data dumped to {file_path}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error dumping data: {str(e)}'))
