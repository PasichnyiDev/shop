from django import forms
from .models import Sale

from products.models import Product


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['selling_price', 'amount']
        labels = {
            'selling_price': 'Ціна продажу',
            'amount': 'Кількість'
        }

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['selling_price'].widget.attrs.update({'class': 'your-css-class'})
        self.fields['amount'].widget.attrs.update({'class': 'your-css-class', 'max': self.initial['max_amount']})
