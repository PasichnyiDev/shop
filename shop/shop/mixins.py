from django.db.models import Sum
from django.utils import timezone
from transactions.models import Sale


class NonCashLimitContextMixin:
    def get_context_data(self, **kwargs):
        month_limit = 90000
        context = super().get_context_data(**kwargs)
        context['month_non_cash_limit'] = float(month_limit) - self.get_non_cash_sales_sum()
        return context

    def get_non_cash_sales_sum(self):
        sales = Sale.objects.all()
        end_date = timezone.now()
        start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        sales.filter(datetime_created__range=(start_date, end_date))
        total_price_sum_non_cash = sales.filter(non_cash=True).aggregate(
            total_price_sum=Sum('total_price'))['total_price_sum']
        return float(total_price_sum_non_cash)
