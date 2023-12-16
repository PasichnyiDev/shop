from django.urls import path

from products import views

app_name = 'products'

urlpatterns = [
    path('create/', views.ProductsCreateView.as_view(), name='products-create'),
    path('create_similar/<int:pk>/', views.CreateSimilarProductView.as_view(), name='create-similar'),
    path('update/<int:pk>/', views.ProductsUpdateView.as_view(), name='products-update'),
    path('detail/<int:pk>/', views.ProductsDetailView.as_view(), name='products-detail'),
    path('delete/<int:pk>/', views.ProductsDeleteView.as_view(), name='products-delete'),
    path('list/', views.ProductsListView.as_view(), name='products-list'),
    path('categories/create/', views.ProductsCategoryCreateView.as_view(), name='category-create')
]
