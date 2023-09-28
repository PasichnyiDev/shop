from django import forms
from .models import Sale, Purchase


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['selling_price', 'amount', 'non_cash']
        labels = {
            'selling_price': 'Ціна продажу',
            'amount': 'Кількість',
            'non_cash': 'Безготівковий розрахунок'
        }
        widgets = {
            'non_cash': forms.CheckboxInput(attrs={'required': False})
        }

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs.update({'max': self.initial['max_amount'], 'min': 1})

    def clean_non_cash(self):
        non_cash = self.cleaned_data.get('non_cash')
        return non_cash


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['purchase_price', 'amount', 'non_cash']
        labels = {
            'purchase_price': 'Ціна закупівлі',
            'amount': 'Кількість',
            'non_cash': 'Безготівковий розрахунок'
        }
        widgets = {
            'non_cash': forms.CheckboxInput(attrs={'required': False})
        }

    def __init__(self, *args, **kwargs):
        super(PurchaseForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs.update({'min': self.initial['min_amount']})
