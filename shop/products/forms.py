from django import forms
from .models import Product, ProductCategory


class ProductsCreateForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['article', 'name', 'brand', 'color', 'size', 'purchase_price',
                  'selling_price', 'in_stock_amount', 'category']
        labels = {
            'article': 'Артикул',
            'name': 'Назва',
            'brand': 'Бренд',
            'color': 'Колір',
            'size': 'Розмір',
            'purchase_price': 'Ціна закупівлі',
            'selling_price': 'Ціна продажу',
            'in_stock_amount': 'В наявності',
            'category': 'Категорія',
        }
        widgets = {
            'in_stock_amount': forms.NumberInput(attrs={'min': 1}),
            'category': forms.Select(),
            'purchase_price': forms.TextInput(attrs={'type': 'number', 'step': '0.01'}),
            'selling_price': forms.TextInput(attrs={'type': 'number', 'step': '0.01'}),
        }


class ProductsCategoryCreateForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name',]
        labels = {
            'name': 'Назва категорії',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')

        if not name:
            raise forms.ValidationError('Це поле обов\'язкове для заповнення.')

        if ProductCategory.objects.filter(name=name).exists():
            raise forms.ValidationError('Категорія з такою назвою вже існує.')

        return name
