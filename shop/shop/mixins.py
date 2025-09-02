from django.db.models import Sum
from django.db.models.query import QuerySet
from django.utils import timezone
from transactions.models import Sale


class NonCashLimitContextMixin:
    def get_context_data(self, **kwargs):
        month_limit = 92000
        context = super().get_context_data(**kwargs)
        non_cash_sales_sum = self.get_non_cash_sales_sum()
        if non_cash_sales_sum:
            context['month_non_cash_limit'] = float(month_limit) - self.get_non_cash_sales_sum()
        else:
            context['month_non_cash_limit'] = float(month_limit)
        return context

    def get_non_cash_sales_sum(self):
        sales = Sale.objects.all()
        sales = sales.filter(is_active=True)
        if sales:
            end_date = timezone.now()
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filtered_sales = sales.filter(datetime_created__range=(start_date, end_date))
            total_price_sum_non_cash = filtered_sales.filter(non_cash=True).aggregate(
                total_price_sum=Sum('total_price'))['total_price_sum']
            if total_price_sum_non_cash:
                return float(total_price_sum_non_cash)
            return 0
        return 0


class TitleMixin:
    title = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class FilterQuerySetByPeriodMixin:

    @staticmethod
    def filter_queryset_by_period(period: str, queryset: QuerySet):
        relevant_period_names = [
            "week",
            "month",
            "quarter",
            "year",
            "day",
            "current_week",
            "current_month",
            "current_year",
        ]
        assert period in relevant_period_names

        end_date = timezone.now()

        if period == "week":
            start_date = end_date - timezone.timedelta(days=7)
        elif period == "month":
            start_date = end_date - timezone.timedelta(days=30)
        elif period == "quarter":
            start_date = end_date - timezone.timedelta(days=90)
        elif period == "year":
            start_date = end_date - timezone.timedelta(days=365)
        elif period == "day":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "current_week":
            day_of_week = end_date.weekday()
            days_until_monday = day_of_week
            start_of_week = end_date - timezone.timedelta(days=days_until_monday)
            start_date = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "current_month":
            start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = end_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return queryset.filter(datetime_created__range=(start_date, end_date))

    @staticmethod
    def filter_queryset_by_dates(start_date, end_date, queryset):
        if start_date and end_date:
            queryset = queryset.filter(datetime_created__date__gte=start_date, datetime_created__date__lte=end_date)
        return queryset
