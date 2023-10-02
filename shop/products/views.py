from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, DeleteView
from .models import Product, ProductCategory
from .forms import ProductsCreateForm, ProductsCategoryCreateForm

from shop.mixins import NonCashLimitContextMixin, TitleMixin
from transactions.models import Sale, Purchase


class ProductsCreateView(TitleMixin, NonCashLimitContextMixin, CreateView):
    model = Product
    form_class = ProductsCreateForm
    template_name = 'products-create.html'
    success_url = reverse_lazy('products:products-list')
    title = 'Створити товар'


class ProductsDetailView(TitleMixin, NonCashLimitContextMixin, DetailView):
    model = Product
    template_name = 'products-detail.html'
    context_object_name = 'product'
    title = 'Інформація про товар'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:

            context["object"] = self.object
            context_object_name = self.get_context_object_name(self.object)

            if context_object_name:
                context[context_object_name] = self.object

            context['product_have_transactions'] = self.product_have_transactions()
            context['product_have_sales'] = self.product_have_sales()
            context['product_have_purchases'] = self.product_have_purchases()

        return context

    def product_have_sales(self):
        return Sale.objects.filter(product__id=self.object.pk).count() > 0

    def product_have_purchases(self):
        return Purchase.objects.filter(product__id=self.object.pk).count() > 0

    def product_have_transactions(self):
        return self.product_have_sales() or self.product_have_purchases()


class ProductsDeleteView(TitleMixin, NonCashLimitContextMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('products:products-list')
    template_name = 'products-confirm-delete.html'
    title = 'Підтвердження видалення'


class ProductsListView(TitleMixin, NonCashLimitContextMixin, ListView):
    model = Product
    template_name = 'products-list.html'
    context_object_name = 'products'
    title = 'Список товарів'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.all()

        category_id = self.request.GET.get('category')
        if category_id:
            context['products'] = context['products'].filter(category__id=category_id)

        context['search_bar'] = self.check_search_bar()
        context['add_product'] = True
        context['add_category'] = True
        context['is_transactions'] = self.check_transactions()
        context['sales'] = self.check_sales()
        context['purchases'] = self.check_purchases()

        search_query = self.request.GET.get('search')
        if search_query:
            result = context['products'].filter(
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
            if not result:
                result = context['products'].filter(
                Q(article__icontains=search_query.capitalize()) |
                Q(name__icontains=search_query.capitalize()) |
                Q(brand__icontains=search_query.capitalize()) |
                Q(color__icontains=search_query.capitalize()) |
                Q(size__icontains=search_query.capitalize()) |
                Q(purchase_price__icontains=search_query.capitalize()) |
                Q(selling_price__icontains=search_query.capitalize()) |
                Q(in_stock_amount__icontains=search_query.capitalize()) |
                Q(category__name__icontains=search_query.capitalize())
            )
            if result:
                context['products'] = result

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

    @staticmethod
    def check_search_bar():
        if Product.objects.last():
            return True
        return False


class ProductsCategoryCreateView(TitleMixin, NonCashLimitContextMixin, CreateView):
    model = ProductCategory
    form_class = ProductsCategoryCreateForm
    template_name = 'products-category-create.html'
    success_url = reverse_lazy('products:products-list')
    title = 'Створити категорію'
