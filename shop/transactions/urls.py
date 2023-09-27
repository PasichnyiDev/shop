from django.urls import path

from transactions import views

app_name = 'transactions'

urlpatterns = [
    path('sales/create/<int:product_id>/', views.SalesCreateView.as_view(), name='sales-create'),
    path('sales/detail/<int:sales_id>/', views.SalesDetailView, name='sales-detail'),
    path('sales/delete/<int:sales_id>/', views.SalesDeleteView, name='sales-delete'),
    path('sales/list/', views.SalesListView.as_view(), name='sales-list'),
    path('purchases/create/', views.PurchasesCreateView, name='purchases-create'),
    path('purchases/detail/<int:purchases_id>/', views.PurchasesDetailView, name='purchases-detail'),
    path('purchases/delete/<int:purchases_id>/', views.PurchasesDeleteView, name='purchases-delete'),
    path('list/', views.TransactionsListView, name='transactions-list')
]
