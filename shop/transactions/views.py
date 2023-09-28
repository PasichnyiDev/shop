from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models.query import QuerySet
from django.views.generic import CreateView, ListView, DetailView, DeleteView

from shop.mixins import NonCashLimitContextMixin

from products.models import Product
from .models import Sale, Purchase
from .forms import SaleForm, PurchaseForm


class FilterQuerySetByPeriodMixin:

    @staticmethod
    def filter_queryset_by_period(period: str, queryset: QuerySet):
        relevant_period_names = [
            "week",
            "month",
            "quarter",
            "year",
            "day",
            "current_week",
            "current_month",
            "current_year",
        ]
        assert period in relevant_period_names

        end_date = timezone.now()

        if period == "week":
            start_date = end_date - timezone.timedelta(days=7)
        elif period == "month":
            start_date = end_date - timezone.timedelta(days=30)
        elif period == "quarter":
            start_date = end_date - timezone.timedelta(days=90)
        elif period == "year":
            start_date = end_date - timezone.timedelta(days=365)
        elif period == "day":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "current_week":
            day_of_week = end_date.weekday()
            days_until_monday = day_of_week
            start_of_week = end_date - timezone.timedelta(days=days_until_monday)
            start_date = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "current_month":
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return queryset.filter(datetime_created__range=(start_date, end_date))


class SalesCreateView(NonCashLimitContextMixin, CreateView):
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
        form.instance.discount = round(
            ((form.instance.product.selling_price - form.instance.selling_price) * form.instance.amount), 2
        )
        form.instance.total_price = round((form.instance.selling_price * form.instance.amount), 2)
        response = super().form_valid(form)
        form.instance.non_cash = form.cleaned_data['non_cash']
        form.instance.product.in_stock_amount -= form.instance.amount
        form.instance.product.save()
        return response

    def get_product_from_route(self):
        return Product.objects.get(pk=self.kwargs['product_id'])


class SalesDetailView(NonCashLimitContextMixin, DetailView):
    model = Sale
    template_name = 'sales-detail.html'
    context_object_name = 'sale'
    pk_url_kwarg = 'sale_id'


class SalesDeleteView(NonCashLimitContextMixin, DeleteView):
    model = Sale
    success_url = reverse_lazy('products:products-list')
    template_name = 'sales-confirm-delete.html'
    pk_url_kwarg = 'sale_id'

    def form_valid(self, form):
        sale = self.get_object()
        product = sale.product

        product.in_stock_amount += sale.amount
        product.save()

        return super().form_valid(form)


class SalesListView(NonCashLimitContextMixin, FilterQuerySetByPeriodMixin, ListView):
    model = Sale
    template_name = 'sales-list.html'
    context_object_name = 'sales'

    def get_queryset(self):
        period = self.request.GET.get("period")
        queryset = self.model.objects.all()
        if period:
            queryset = self.filter_queryset_by_period(period=period, queryset=queryset)

        return queryset


class PurchasesCreateView(NonCashLimitContextMixin, CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchases-create.html'
    success_url = reverse_lazy('products:products-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['product'] = self.get_product_from_route()
        return context

    def get_initial(self):
        initial = {'min_amount': 1}
        return initial

    def form_valid(self, form):
        form.instance.product = self.get_product_from_route()
        form.instance.total_price = round((form.instance.purchase_price * form.instance.amount), 2)
        response = super().form_valid(form)
        form.instance.non_cash = form.cleaned_data['non_cash']
        form.instance.product.in_stock_amount += form.instance.amount
        form.instance.product.save()
        return response

    def get_product_from_route(self):
        return Product.objects.get(pk=self.kwargs['product_id'])


class PurchasesDetailView(NonCashLimitContextMixin, DetailView):
    model = Purchase
    template_name = 'purchases-detail.html'
    context_object_name = 'purchase'
    pk_url_kwarg = 'purchase_id'


class PurchasesDeleteView(NonCashLimitContextMixin, DeleteView):
    model = Purchase
    success_url = reverse_lazy('products:products-list')
    template_name = 'purchases-confirm-delete.html'
    pk_url_kwarg = 'purchase_id'

    def form_valid(self, form):
        sale = self.get_object()
        product = sale.product

        product.in_stock_amount -= sale.amount
        product.save()

        return super().form_valid(form)


class PurchasesListView(NonCashLimitContextMixin, FilterQuerySetByPeriodMixin, ListView):
    model = Purchase
    template_name = 'purchases-list.html'
    context_object_name = 'purchases'

    def get_queryset(self):
        period = self.request.GET.get("period")
        queryset = self.model.objects.all()
        if period:
            queryset = self.filter_queryset_by_period(period=period, queryset=queryset)

        return queryset


class TransactionsListView(NonCashLimitContextMixin, FilterQuerySetByPeriodMixin, ListView):

    template_name = 'transactions-list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        period = self.request.GET.get("period")
        sales = Sale.objects.all()
        purchases = Purchase.objects.all()
        if period:
            sales = self.filter_queryset_by_period(period=period, queryset=sales)
            purchases = self.filter_queryset_by_period(period=period, queryset=purchases)
        combined_queryset = list(sales) + list(purchases)
        combined_queryset.sort(key=lambda x: x.datetime_created, reverse=True)
        return combined_queryset
