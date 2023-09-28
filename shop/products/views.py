from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, DeleteView
from .models import Product, ProductCategory
from .forms import ProductsCreateForm, ProductsCategoryCreateForm

from shop.mixins import NonCashLimitContextMixin
from transactions.models import Sale, Purchase


class ProductsCreateView(NonCashLimitContextMixin, CreateView):
    model = Product
    form_class = ProductsCreateForm
    template_name = 'products-create.html'
    success_url = reverse_lazy('products:products-list')


class ProductsDetailView(NonCashLimitContextMixin, DetailView):
    model = Product
    template_name = 'products-detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:

            context["object"] = self.object
            context_object_name = self.get_context_object_name(self.object)

            if context_object_name:
                context[context_object_name] = self.object

            # Sales
            sales = Sale.objects.filter(product__id=self.object.id)
            context["sales"] = sales

            total_price_sum_non_cash = sales.filter(non_cash=True).aggregate(
                total_price_sum=Sum('total_price'))['total_price_sum']
            if total_price_sum_non_cash:
                context['total_price_sum_non_cash'] = total_price_sum_non_cash

            total_price_sum_cash = sales.filter(non_cash=False).aggregate(
                total_price_sum=Sum('total_price'))['total_price_sum']
            if total_price_sum_cash:
                context['total_price_sum_cash'] = total_price_sum_cash
            if total_price_sum_cash and total_price_sum_non_cash:
                total_price_sum = total_price_sum_non_cash + total_price_sum_cash
                context['total_price_sum'] = total_price_sum
            amount_sum = sales.aggregate(amount_sum=Sum('amount'))['amount_sum']
            if amount_sum:
                context['amount_sum'] = amount_sum

        return context


class ProductsDeleteView(NonCashLimitContextMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('products:products-list')
    template_name = 'products-confirm-delete.html'


class ProductsListView(NonCashLimitContextMixin, ListView):
    model = Product
    template_name = 'products-list.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.all()

        category_id = self.request.GET.get('category')
        if category_id:
            context['products'] = context['products'].filter(category__id=category_id)

        context['search_bar'] = True
        context['add_product'] = True
        context['add_category'] = True
        context['is_transactions'] = self.check_transactions()
        context['sales'] = self.check_sales()
        context['purchases'] = self.check_purchases()

        search_query = self.request.GET.get('search')
        if search_query:
            context['products'] = context['products'].filter(
                Q(article__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(brand__icontains=search_query) |
                Q(color__icontains=search_query) |
                Q(size__icontains=search_query) |
                Q(purchase_price__icontains=search_query) |
                Q(selling_price__icontains=search_query) |
                Q(in_stock_amount__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        return context

    @staticmethod
    def check_transactions():
        return Sale.objects.last() or Purchase.objects.last()

    @staticmethod
    def check_sales():
        if Sale.objects.last():
            return True
        return False

    @staticmethod
    def check_purchases():
        if Purchase.objects.last():
            return True
        return False


class ProductsCategoryCreateView(NonCashLimitContextMixin, CreateView):
    model = ProductCategory
    form_class = ProductsCategoryCreateForm
    template_name = 'products-category-create.html'
    success_url = reverse_lazy('products:products-list')
