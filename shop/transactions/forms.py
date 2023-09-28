from django import forms
from .models import Sale


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
        self.fields['selling_price'].widget.attrs.update({'class': 'your-css-class'})
        self.fields['amount'].widget.attrs.update({'class': 'your-css-class', 'max': self.initial['max_amount']})

    def clean_non_cash(self):
        non_cash = self.cleaned_data.get('non_cash')
        return non_cash
