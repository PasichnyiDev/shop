from django.urls import path

from transactions import views

app_name = 'transactions'

urlpatterns = [
    path('sales/create/<int:product_id>/', views.SalesCreateView.as_view(), name='sales-create'),
    path('sales/detail/<int:sale_id>/', views.SalesDetailView.as_view(), name='sales-detail'),
    path('sales/delete/<int:sale_id>/', views.SalesDeleteView.as_view(), name='sales-delete'),
    path('sales/list/', views.SalesListView.as_view(), name='sales-list'),
    path('purchases/create/<int:product_id>/', views.PurchasesCreateView.as_view(), name='purchases-create'),
    path('purchases/detail/<int:purchase_id>/', views.PurchasesDetailView.as_view(), name='purchases-detail'),
    path('purchases/delete/<int:purchase_id>/', views.PurchasesDeleteView.as_view(), name='purchases-delete'),
    path('purchases/list/', views.PurchasesListView.as_view(), name='purchases-list'),
    path('list/', views.TransactionsListView.as_view(), name='transactions-list')
]
