from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')
    inlines = [OrderItemInline]
    actions = ['mark_as_paid', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    date_hierarchy = 'created_at'


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    list_filter = ('order__status',)
    search_fields = ('order__user__username', 'order__user__email', 'product__name')
    date_hierarchy = 'created_at'
    actions = ['mark_as_cancelled']


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)