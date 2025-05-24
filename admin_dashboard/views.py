from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Sum, Q
from django.utils import timezone
from users.models import CustomUser
from orders.models import Order, OrderItem
from products.models import Product, Category
from custom_jerseys.models import CustomJerseyOrder
from chat.models import ChatRoom, Message


@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # Date ranges
    today = timezone.now().date()
    last_7_days = today - timezone.timedelta(days=7)
    last_30_days = today - timezone.timedelta(days=30)

    # User statistics
    total_users = CustomUser.objects.count()
    new_users_today = CustomUser.objects.filter(date_joined__date=today).count()
    new_users_week = CustomUser.objects.filter(date_joined__date__gte=last_7_days).count()

    # Order statistics
    total_orders = Order.objects.count()
    today_orders = Order.objects.filter(created_at__date=today).count()
    weekly_orders = Order.objects.filter(created_at__date__gte=last_7_days).count()

    # Sales statistics
    total_sales = Order.objects.aggregate(total=Sum('order_total'))['total'] or 0
    today_sales = Order.objects.filter(created_at__date=today).aggregate(total=Sum('order_total'))['total'] or 0
    weekly_sales = Order.objects.filter(created_at__date__gte=last_7_days).aggregate(total=Sum('order_total'))[
                       'total'] or 0

    # Custom jersey orders
    custom_orders = CustomJerseyOrder.objects.count()
    pending_custom_orders = CustomJerseyOrder.objects.filter(status='P').count()

    # Recent orders (last 10)
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    # Recent custom jersey orders
    recent_custom_orders = CustomJerseyOrder.objects.select_related('user').order_by('-created_at')[:5]

    # Product statistics
    low_stock_products = Product.objects.filter(stock__lt=10).count()
    out_of_stock_products = Product.objects.filter(stock=0).count()

    # Chat statistics
    active_chats = ChatRoom.objects.filter(is_active=True).count()
    unread_messages = Message.objects.filter(is_read=False).exclude(sender=request.user).count()

    context = {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'total_orders': total_orders,
        'today_orders': today_orders,
        'weekly_orders': weekly_orders,
        'total_sales': total_sales,
        'today_sales': today_sales,
        'weekly_sales': weekly_sales,
        'custom_orders': custom_orders,
        'pending_custom_orders': pending_custom_orders,
        'recent_orders': recent_orders,
        'recent_custom_orders': recent_custom_orders,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'active_chats': active_chats,
        'unread_messages': unread_messages,
    }

    return render(request, 'admin_dashboard/dashboard.html', context)
