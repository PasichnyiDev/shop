from django.urls import path

import views

urlpatterns = [
    path('create/', views.ProductsCreateView, name='products-create'),
    path('detail/<int:product_id>/', views.ProductsDetailView, name='products-detail'),
    path('delete/<int:product_id>/', views.ProductsDeleteView, name='products-delete'),
    path('list/', views.ProductsListView, name='products-list'),
]
