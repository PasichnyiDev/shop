from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, DeleteView
from .models import Product, ProductCategory
from .forms import ProductsCreateForm


class ProductsCreateView(CreateView):
    model = Product
    form_class = ProductsCreateForm
    template_name = 'products-create.html'
    success_url = reverse_lazy('products:products-list')


class ProductsDetailView(DetailView):
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
            context['same_products'] = Product.objects.filter(
                name=self.object.name, brand=self.object.brand
            ).exclude(id=self.object.id)

        return context


class ProductsDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('products:products-list')
    template_name = 'products-confirm-delete.html'


class ProductsListView(ListView):
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

