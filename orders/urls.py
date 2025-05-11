from django.urls import path
from .views import OrderListView, OrderDetailView, OrderCreateView, OrderStatusUpdateView


urlpatterns = [
    path('', OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/update-status/', OrderStatusUpdateView.as_view(), name='order_status_update'),
]
