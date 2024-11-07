from datetime import datetime, timedelta
from typing import Dict, Optional, Union

from django.db.models import Count, Q, Sum, Avg
from django.db.models.functions import ExtractDay, ExtractYear, ExtractMonth
from django.utils import timezone

from orders.models import Order
from reviews.models import VendorReview

from .models import Vendor


def vendor_order_summary(
    vendor: Vendor,
    *,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    filter_type: Optional[str] = None,
) -> Dict[str, Union[int, Dict[str, int]]]:
    """
    Fetches and aggregates order statistics for a given vendor within a specified date range.

    Args:
        vendor (Vendor): The vendor for whom to fetch order statistics.
        filter_type (Optional[str]): Filter type, either 'year' or 'month'. Defaults to None.
        start_date (Optional[datetime]): The starting date of the range. Defaults to None.
        end_date (Optional[datetime]): The ending date of the range. Defaults to None.

    Returns:
        Dict[str, Union[int, Dict[str, int]]]: A dictionary containing:
            - 'total_order_count': Total number of orders in the specified range.
            - 'completed_count': Number of orders with status 'Completed'.
            - 'cancelled_count': Number of orders with status 'Cancelled'.
            - 'filter_info': Year and/or month details if filter_type is specified.
    """

    orders = Order.objects.filter(vendor=vendor, is_ordered=True).order_by(
        "-created_at"
    )

    if start_date:
        orders = orders.filter(created_at__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__lte=end_date)

    filter_info = {}
    current_year = timezone.now().year
    current_month = timezone.now().month

    if filter_type == "year":
        orders = orders.filter(created_at__year=current_year)
        filter_info["filter_year"] = current_year
    elif filter_type == "month":
        orders = orders.filter(
            created_at__year=current_year, created_at__month=current_month
        )
        filter_info["filter_year"] = current_year
        filter_info["filter_month"] = current_month

    order_summary: Dict[str, int] = orders.aggregate(
        total_order_count=Count("id"),
        completed_count=Count("id", filter=Q(status="Completed")),
        cancelled_count=Count("id", filter=Q(status="Cancelled")),
    )

    

    if filter_info:
        order_summary["filter_info"] = filter_info

    return order_summary


def vendor_total_revenue(vendor: Vendor):
    orders = Order.objects.filter(vendor=vendor, is_ordered=True, status="Completed").order_by('created_at')


    now = timezone.now()
    
    start_date = now - timedelta(days=29)
    last_30days = [(start_date + timedelta(days=i)).strftime("%d-%m") for i in range(30)]
   

    daily_revenue = (
        orders.filter(
            created_at__range = (start_date, now))
            .annotate(day=ExtractDay('created_at'), month=ExtractMonth('created_at'), year=ExtractYear('created_at'))
            .values('day', 'month', 'year')
            .annotate(total_revenue=Sum('total'))
            .order_by('year', 'month', 'day')
    )
    
    
    last_12months = []
    for i in range(12):
        month = (now.month - i - 1) % 12 + 1
        year = now.year + ((now.month-i-1)//12)
        last_12months.insert(0,(month, year))
        
    
    query = Q()

    for month, year in last_12months:
        query |= Q(created_at__year=year, created_at__month=month)


    monthly_revenue = (
        orders.filter(query)
            .annotate(month=ExtractMonth('created_at'), year=ExtractYear('created_at'))
            .values('month', 'year')  
            .annotate(total_revenue=Sum('total')) 
            .order_by('month')
    )

    
    
    return list(daily_revenue), list(monthly_revenue), last_12months, last_30days



def get_vendor_review(vendor: Vendor) -> Dict[str, int]:
    rated_orders = VendorReview.objects.filter(order__vendor=vendor, rating__isnull=False)

    average_rating = rated_orders.aggregate(
        avg_rating = Avg('rating'),
        rating_count = Count('rating'),
        one_rating = Count('rating', filter=Q(rating=1)),
        two_rating = Count('rating', filter=Q(rating=2)),
        three_rating = Count('rating', filter=Q(rating=3)),
        four_rating = Count('rating', filter=Q(rating=4)),
        five_rating = Count('rating', filter=Q(rating=5))
    )

    return average_rating