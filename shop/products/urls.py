from django.urls import path

from products import views

app_name = 'products'

urlpatterns = [
    path('create/', views.ProductsCreateView.as_view(), name='products-create'),
    path('detail/<int:pk>/', views.ProductsDetailView.as_view(), name='products-detail'),
    path('delete/<int:pk>/', views.ProductsDeleteView.as_view(), name='products-delete'),
    path('list/', views.ProductsListView.as_view(), name='products-list'),
]
