from django.urls import path
from .views import GeneralStatView

urlpatterns = [
    path('main/', GeneralStatView.as_view(), name='stat-main'),
]
