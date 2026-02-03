import csv
import json
from datetime import timedelta

from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib import admin
from django.db.models import Sum, F
from django.db.models.functions import TruncDay
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.urls import path
from django import forms

from .models import (
    Customer, Product, Order, OrderItem,
    Payment, Shipment, Outbox
)

# -------------------------------------------------------------------
# 1. Custom Admin Site with Dashboard + Custom URL
# -------------------------------------------------------------------
class MyAdminSite(admin.AdminSite):
    site_header = "E-Commerce Management Dashboard"

    def index(self, request, extra_context=None):
        last_week = timezone.now() - timedelta(days=7)

        # --- A. KPI Calculations ---
        total_revenue = (
            Order.objects.filter(complete=True)
            .aggregate(Sum('total_due'))['total_due__sum'] or 0
        )
        customer_count = Customer.objects.count()

        # --- B. Sales Chart Data ---
        sales_data = (
            Order.objects.filter(complete=True)
            .annotate(day=TruncDay('date_order'))
            .values('day')
            .annotate(total=Sum('total_due'))
            .order_by('day')[:7]
        )
        chart_data = [
            {"day": x['day'].strftime('%b %d'), "total": float(x['total'])}
            for x in sales_data
        ]

        # --- C. Top Products ---
        top_products = (
            OrderItem.objects.values('product__name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:5]
        )

        # --- D. Low Stock ---
        low_stock_products = Product.objects.filter(
            stock_quantity__lt=5
        ).order_by('stock_quantity')

        # --- E. Recent Transactions ---
        recent_payments = (
            Payment.objects.select_related('order', 'order__customer')
            .order_by('-created_at')[:5]
        )

        extra_context = extra_context or {}
        extra_context.update({
            'total_revenue': total_revenue,
            'customer_count': customer_count,
            'chart_data': json.dumps(chart_data),
            'top_products': top_products,
            'low_stock_products': low_stock_products,
            'low_stock_count': low_stock_products.count(),
            'recent_payments': recent_payments,
        })
        return super().index(request, extra_context)

    # --- Custom URL for AJAX (fetch order total_due) ---
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get_order_total/<int:order_id>/', self.admin_view(get_order_total)),
        ]
        return custom_urls + urls


# Instantiate once
mysite = MyAdminSite(name='myadmin')
mysite.index_template = 'admin/index.html'


# -------------------------------------------------------------------
# 2. Utility Views
# -------------------------------------------------------------------
def get_order_total(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        return JsonResponse({'total_due': float(order.total_due)})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)


# -------------------------------------------------------------------
# 3. CSV Export Action
# -------------------------------------------------------------------
@admin.action(description="Export selected orders to CSV")
def export_orders_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Date', 'Status', 'Total Due'])
    for order in queryset:
        writer.writerow([
            order.id,
            str(order.customer),
            order.date_order.strftime("%Y-%m-%d %H:%M"),
            "Complete" if order.complete else "Pending",
            order.total_due,
        ])
    return response


# -------------------------------------------------------------------
# 4. Inlines
# -------------------------------------------------------------------
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1   # ensures management form is rendered
    readonly_fields = ['price_at_purchase']
    raw_id_fields = ['product']


class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [CustomerInline]


# -------------------------------------------------------------------
# 5. Product Admin
# -------------------------------------------------------------------
@admin.register(Product, site=mysite)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_price', 'stock_quantity']
    list_editable = ['current_price', 'stock_quantity']
    search_fields = ['name']


# -------------------------------------------------------------------
# 6. Order Admin
# -------------------------------------------------------------------
@admin.register(Order, site=mysite)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'date_order', 'complete', 'total_due']
    list_filter = ['complete', 'date_order']
    inlines = [OrderItemInline]
    actions = [export_orders_to_csv]
    readonly_fields = ['total_due']

    class Media:
        js = ('js/admin_order_calc.js',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        formset.save()
        obj = form.instance
        total = obj.items.aggregate(
            total=Sum(F('quantity') * F('price_at_purchase'))
        )['total'] or 0
        obj.total_due = total
        obj.save(update_fields=['total_due'])


# -------------------------------------------------------------------
# 7. Payment Admin with auto-prefill + JS auto-fill
# -------------------------------------------------------------------
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.order_id:
            self.fields['amount'].initial = self.instance.order.total_due


@admin.register(Payment, site=mysite)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentForm
    list_display = ['id', 'order', 'amount', 'method', 'status', 'created_at']

    class Media:
        js = ('js/payment_autofill.js',)  # Injects JS into Add Payment page


# -------------------------------------------------------------------
# 8. Fast register for other models
# -------------------------------------------------------------------
mysite.register(Shipment)
mysite.register(Outbox)

# -------------------------------------------------------------------
# 9. Register User and Group with custom admin site
# -------------------------------------------------------------------
mysite.register(User, CustomUserAdmin)
mysite.register(Group, GroupAdmin)
