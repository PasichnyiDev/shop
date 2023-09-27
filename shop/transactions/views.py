from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .models import Sale
from .forms import SaleForm
from products.models import Product


class SalesCreateView(CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales-create.html'
    success_url = reverse_lazy('products:products-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['product'] = self.get_product_from_route()
        return context

    def get_initial(self):
        initial = {'max_amount': self.get_product_from_route().in_stock_amount}
        return initial

    def form_valid(self, form):
        form.instance.product = self.get_product_from_route()
        form.instance.discount = round((form.instance.product.selling_price - form.instance.selling_price), 2)
        response = super().form_valid(form)
        form.instance.product.in_stock_amount -= form.instance.amount
        form.instance.product.save()
        return response

    def get_product_from_route(self):
        return Product.objects.get(pk=self.kwargs['product_id'])


class SalesDetailView:
    pass


class SalesDeleteView:
    pass


class SalesListView(ListView):
    model = Sale
    template_name = 'sales-list.html'
    context_object_name = 'sales'


class PurchasesCreateView:
    pass


class PurchasesDetailView:
    pass


class PurchasesDeleteView:
    pass


class TransactionsListView:
    pass
