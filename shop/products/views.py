from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from .models import Product, ProductCategory
from .forms import ProductsCreateForm, ProductsCategoryCreateForm, ProductsUpdateForm

from shop.mixins import NonCashLimitContextMixin, TitleMixin
from transactions.models import Sale, Purchase


class ProductsCreateView(TitleMixin, NonCashLimitContextMixin, CreateView):
    model = Product
    form_class = ProductsCreateForm
    template_name = 'products-create.html'
    success_url = reverse_lazy('products:products-list')
    title = 'Створити товар'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Товар створено!')
        return JsonResponse({'success': True})


class ProductsCreateAndPurchaseView(TitleMixin, NonCashLimitContextMixin, CreateView):
    model = Product
    form_class = ProductsCreateForm
    template_name = 'products-create.html'
    success_url = reverse_lazy('products:products-list')
    title = 'Створити та закупити товар'

    def form_valid(self, form):
        response = super().form_valid(form)
        obj = form.instance
        purchase = Purchase.objects.create(
            purchase_price=obj.purchase_price,
            amount=obj.in_stock_amount,
            total_price=round((obj.purchase_price * obj.in_stock_amount), 2),
            product=Product.objects.get(pk=obj.pk)
        )
        purchase.save()
        obj.save()

        return response


class ProductsUpdateView(TitleMixin, NonCashLimitContextMixin, UpdateView):
    model = Product
    form_class = ProductsUpdateForm
    template_name = 'products-update.html'
    success_url = reverse_lazy('products:products-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        context['object'] = product
        return context


class CreateSimilarProductView(NonCashLimitContextMixin, CreateView):
    model = Product
    form_class = ProductsCreateForm
    template_name = 'products-create.html'
    success_url = reverse_lazy('products:products-list')
    title = 'Створити схожий товар'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        context['product_id'] = product.pk
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.creating_similar_product = True
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        obj = form.instance
        purchase = Purchase.objects.create(
            purchase_price=obj.purchase_price,
            amount=obj.in_stock_amount,
            total_price=round((obj.purchase_price * obj.in_stock_amount), 2),
            product=Product.objects.get(pk=obj.pk)
        )
        purchase.save()
        obj.save()
        return response

    def get_initial(self):
        initial = super().get_initial()
        product = Product.objects.get(pk=self.kwargs['pk'])
        initial['article'] = product.article
        initial['category'] = product.category
        initial['name'] = product.name
        initial['brand'] = product.brand
        initial['color'] = product.color
        initial['purchase_price'] = product.purchase_price
        initial['selling_price'] = product.selling_price
        initial['in_stock_amount'] = product.in_stock_amount
        return initial


class ProductsDetailView(TitleMixin, NonCashLimitContextMixin, DetailView):
    model = Product
    template_name = 'products-detail.html'
    context_object_name = 'product'
    title = 'Інформація про товар'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            sizes = self.get_available_sizes()
            context['sizes'] = sizes if len(sizes) >= 1 else None
            context['sizes_out_of_stock'] = self.get_out_of_stock_sizes()
            context["object"] = self.object
            context_object_name = self.get_context_object_name(self.object)

            if context_object_name:
                context[context_object_name] = self.object

            context['product_have_transactions'] = self.product_have_transactions()
            context['product_have_sales'] = self.product_have_sales()
            context['product_have_purchases'] = self.product_have_purchases()

        return context

    def get_available_sizes(self):
        return Product.objects.filter(name=self.object.name).filter(brand=self.object.brand)\
            .filter(color=self.object.color).filter(in_stock_amount__gt=0)

    def get_out_of_stock_sizes(self):
        return Product.objects.filter(name=self.object.name).filter(brand=self.object.brand)\
            .filter(color=self.object.color).filter(in_stock_amount__lt=1)

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
        context['stat'] = True

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

    def check_transactions(self):
        return self.check_sales() or self.check_purchases()

    @staticmethod
    def check_sales():
        sales = Sale.objects.filter(is_active=True)
        if sales.last():
            return True
        return False

    @staticmethod
    def check_purchases():
        purchases = Purchase.objects.filter(is_active=True)
        if purchases.last():
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
