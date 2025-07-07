import datetime

from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.db.models import Sum

from django.views.generic import CreateView, ListView, DetailView, DeleteView, TemplateView

from shop.mixins import TitleMixin, NonCashLimitContextMixin, FilterQuerySetByPeriodMixin

from products.models import Product
from .models import Sale, Purchase
from .forms import SaleForm, PurchaseForm


class SalesCreateView(TitleMixin, NonCashLimitContextMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sales-create.html'
    success_url = reverse_lazy('products:products-list')
    title = 'Створити продажу'

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


class SalesDetailView(TitleMixin, NonCashLimitContextMixin, DetailView):
    model = Sale
    template_name = 'sales-detail.html'
    context_object_name = 'sale'
    pk_url_kwarg = 'sale_id'
    title = 'Інформація про продажу'


class SalesDeleteView(TitleMixin, NonCashLimitContextMixin, DeleteView):
    model = Sale
    success_url = reverse_lazy('products:products-list')
    template_name = 'sales-confirm-delete.html'
    pk_url_kwarg = 'sale_id'
    title = 'Підтвердження видалення продажу'

    def form_valid(self, form):
        sale = self.get_object()
        product = sale.product
        product.in_stock_amount += sale.amount
        product.save()
        success_url = self.get_success_url()
        sale.is_active = False
        sale.save()
        return HttpResponseRedirect(success_url)


class SalesListView(TitleMixin, NonCashLimitContextMixin, FilterQuerySetByPeriodMixin, ListView):
    model = Sale
    template_name = 'sales-list.html'
    context_object_name = 'sales'
    title = 'Список продаж'

    def get_queryset(self):
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        period = self.request.GET.get("period")
        product_id = self.kwargs.get('product_id')
        queryset = self.model.objects.filter(is_active=True)
        if product_id:
            queryset = queryset.filter(product__id=product_id)
        if period:
            queryset = self.filter_queryset_by_period(period=period, queryset=queryset)
        if start_date:
            if not end_date:
                end_date = datetime.date.today()
            queryset = self.filter_queryset_by_dates(start_date=start_date, end_date=end_date, queryset=queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product_id = self.kwargs.get('product_id')
        if product_id:
            context['product_id'] = product_id
        return context


class PurchasesCreateView(TitleMixin, NonCashLimitContextMixin, CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchases-create.html'
    title = 'Створити закупівлю'

    def get_success_url(self):
        pk = self.get_product_from_route().pk
        return reverse_lazy('products:products-detail', kwargs={'pk': pk})

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


class PurchasesDetailView(TitleMixin, NonCashLimitContextMixin, DetailView):
    model = Purchase
    template_name = 'purchases-detail.html'
    context_object_name = 'purchase'
    pk_url_kwarg = 'purchase_id'
    title = 'Інформація про закупівлю'


class PurchasesDeleteView(TitleMixin, NonCashLimitContextMixin, DeleteView):
    model = Purchase
    success_url = reverse_lazy('products:products-list')
    template_name = 'purchases-confirm-delete.html'
    pk_url_kwarg = 'purchase_id'
    title = 'Підтвердження видалення закупівлі'

    def form_valid(self, form):
        purchase = self.get_object()
        product = purchase.product
        product.in_stock_amount -= purchase.amount
        product.save()
        success_url = self.get_success_url()
        purchase.is_active = False
        purchase.save()
        return HttpResponseRedirect(success_url)


class PurchasesListView(TitleMixin, NonCashLimitContextMixin, FilterQuerySetByPeriodMixin, ListView):
    model = Purchase
    template_name = 'purchases-list.html'
    context_object_name = 'purchases'
    title = 'Список закупівель'

    def get_queryset(self):
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        period = self.request.GET.get("period")
        product_id = self.kwargs.get('product_id')
        queryset = self.model.objects.filter(is_active=True)
        if product_id:
            queryset = queryset.filter(product__id=product_id)
        if period:
            queryset = self.filter_queryset_by_period(period=period, queryset=queryset)
        if start_date:
            if not end_date:
                end_date = datetime.date.today()
            queryset = self.filter_queryset_by_dates(start_date=start_date, end_date=end_date, queryset=queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product_id = self.kwargs.get('product_id')
        if product_id:
            context['product_id'] = product_id
        return context


class TransactionsListView(TitleMixin, NonCashLimitContextMixin, FilterQuerySetByPeriodMixin, ListView):
    template_name = 'transactions-list.html'
    context_object_name = 'transactions'
    title = 'Список транзакцій'
    paginate_by = 20

    def get_queryset(self):

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        period = self.request.GET.get("period")
        product_id = self.kwargs.get('product_id')

        sales = Sale.objects.filter(is_active=True)
        purchases = Purchase.objects.filter(is_active=True)

        if product_id:
            sales = sales.filter(product__id=product_id)
            purchases = purchases.filter(product__id=product_id)

        if period:
            sales = self.filter_queryset_by_period(period=period, queryset=sales)
            purchases = self.filter_queryset_by_period(period=period, queryset=purchases)

        if start_date:
            if not end_date:
                end_date = datetime.date.today()
            sales = self.filter_queryset_by_dates(start_date=start_date, end_date=end_date, queryset=sales)
            purchases = self.filter_queryset_by_dates(start_date=start_date, end_date=end_date, queryset=purchases)

        combined_queryset = list(sales) + list(purchases)
        combined_queryset.sort(key=lambda x: x.datetime_created, reverse=True)

        return combined_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id')
        if product_id:
            context['product_id'] = product_id
        return context


class TransactionsTotalView(TitleMixin, NonCashLimitContextMixin, FilterQuerySetByPeriodMixin, TemplateView):
    template_name = 'transactions-total.html'
    title = 'Узагальнені відомості про транзакції'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        product_id = self.kwargs.get('product_id')
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        period = self.request.GET.get("period")
        sales = Sale.objects.filter(is_active=True)
        purchases = Purchase.objects.filter(is_active=True)
        if product_id:
            context['product_id'] = product_id
            context['product'] = Product.objects.get(pk=product_id)
            sales = sales.filter(product__id=product_id)
            purchases = purchases.filter(product__id=product_id)

        if period:
            sales = self.filter_queryset_by_period(period=period, queryset=sales)
            purchases = self.filter_queryset_by_period(period=period, queryset=purchases)

        if start_date:
            if not end_date:
                end_date = datetime.date.today()
            sales = self.filter_queryset_by_dates(start_date=start_date, end_date=end_date, queryset=sales)
            purchases = self.filter_queryset_by_dates(start_date=start_date, end_date=end_date, queryset=purchases)

        context['sales_total_non_cash_price_sum'] = self.get_total_price_sum(queryset=sales, non_cash=True)
        context['sales_total_cash_price_sum'] = self.get_total_price_sum(queryset=sales, non_cash=False)
        context['sales_total_sum'] = context['sales_total_non_cash_price_sum'] + context['sales_total_cash_price_sum']
        context['sales_total_amount_sum'] = self.get_total_amount_sum(queryset=sales)

        context['purchases_total_non_cash_price_sum'] = self.get_total_price_sum(queryset=purchases, non_cash=True)
        context['purchases_total_cash_price_sum'] = self.get_total_price_sum(queryset=purchases, non_cash=False)
        context['purchases_total_sum'] = context['purchases_total_non_cash_price_sum'] + \
                                         context['purchases_total_cash_price_sum']
        context['purchases_total_amount_sum'] = self.get_total_amount_sum(queryset=purchases)
        return context

    @staticmethod
    def get_total_price_sum(queryset, non_cash):
        result = queryset.filter(non_cash=non_cash).aggregate(
                total_price_sum=Sum('total_price'))['total_price_sum']
        return result if result else 0

    @staticmethod
    def get_total_amount_sum(queryset):
        result = queryset.aggregate(amount_sum=Sum('amount'))['amount_sum']
        return result if result else 0
