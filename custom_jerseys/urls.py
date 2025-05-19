from django.urls import path
from .views import (
    CustomJerseyOrderListView, CustomJerseyOrderDetailView,
    CustomJerseyOrderCreateView, CustomJerseyStatusUpdateView
)


urlpatterns = [
    path('', CustomJerseyOrderListView.as_view(), name='custom_jersey_list'),
    path('<int:pk>/', CustomJerseyOrderDetailView.as_view(), name='custom_jersey_detail'),
    path('create/<int:pk>/', CustomJerseyOrderCreateView.as_view(), name='custom_jersey_create'),
    path('<int:pk>/update-status/', CustomJerseyStatusUpdateView.as_view(), name='custom_jersey_status_update'),
]
