from accounts.models import User
from django.db.models import Count, Q, Sum, F
from orders.models import OrderedFood


def customer_count():
    users = User.objects.filter(is_active=True)

    users_count = users.aggregate(
        customer_count = Count('id', filter=Q(role=User.CUSTOMER)),
        vendor_count = Count('id', filter=Q(role=User.VENDOR))
    )

    return users_count


def top_10_products():
    top_products = (
        OrderedFood.objects
        .filter(order__is_ordered=True)
        .values('fooditem')  
        .annotate(
            total_quantity_sold=Sum('quantity'),
            food_title=F('fooditem__food_title'),
            vendor_name=F('fooditem__vendor__vendor_name'),
        )
        .order_by('-total_quantity_sold')[:10]
    )
    print(top_products)
    return top_products

