from shop.mixins import TitleMixin, NonCashLimitContextMixin
from django.views.generic.base import TemplateView
from products.models import Product


class GeneralStatView(NonCashLimitContextMixin, TitleMixin, TemplateView):
    title = 'Загальна статистика'
    template_name = 'stat-main.html'

    def get_context_data(self, **kwargs):
        context = super(GeneralStatView, self).get_context_data()
        context['total_purchase_price'] = self.get_total_price(purchase=True)
        context['total_selling_price'] = self.get_total_price(purchase=False)
        context['total_products_amount'] = self.get_total_products_amount()
        context['potential_profit'] = context['total_selling_price'] - context['total_purchase_price']
        return context

    @staticmethod
    def get_total_price(purchase: bool):
        products = Product.objects.all()
        total = 0
        for i in products:
            if purchase:
                total += i.in_stock_amount * i.purchase_price
            else:
                total += i.in_stock_amount * i.selling_price
        return total

    @staticmethod
    def get_total_products_amount():
        return Product.objects.all().count()






