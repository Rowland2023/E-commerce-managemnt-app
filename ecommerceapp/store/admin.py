import csv
import json
import requests
from datetime import timedelta

from django.utils import timezone
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib import admin
from django.db.models import Sum, F
from django.db.models.functions import TruncDay
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.urls import path
from django import forms
from django.http import HttpResponseRedirect

from .models import (
    Customer, Product, Order, OrderItem,
    Payment, Shipment, Outbox, EmployeeLink, InvoiceLink
)

# -------------------------------------------------------------------
# 1. External Service Link Admins
# -------------------------------------------------------------------

class EmployeeLinkAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect('/employee')

class InvoiceLinkAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def changelist_view(self, request, extra_context=None):
        return HttpResponseRedirect('/api/v1/invoices/docs')

# -------------------------------------------------------------------
# 2. Custom Admin Site (Dashboard & KPI Logic)
# -------------------------------------------------------------------

class MyAdminSite(admin.AdminSite):
    site_header = "E-Commerce Management Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('employee-stats/', self.admin_view(self.employee_stats_view), name="employee-stats"),
            path('get_order_total/<int:order_id>/', self.admin_view(get_order_total)),
        ]
        return custom_urls + urls

    def employee_stats_view(self, request):
        try:
            response = requests.get("http://employee_service:3000/employee", timeout=2)
            employee_data = response.json()
        except Exception:
            employee_data = {"error": "Node.js Service Offline"}

        context = {
            **self.each_context(request),
            'title': 'Employee Management System',
            'data': employee_data,
        }
        return render(request, 'admin/employee_stats.html', context)    

    def index(self, request, extra_context=None):
        # KPI & Sales Logic
        total_revenue = Order.objects.filter(complete=True).aggregate(Sum('total_due'))['total_due__sum'] or 0
        customer_count = Customer.objects.count()

        sales_data = (
            Order.objects.filter(complete=True)
            .annotate(day=TruncDay('date_order'))
            .values('day')
            .annotate(total=Sum('total_due'))
            .order_by('day')[:7]
        )
        chart_data = [{"day": x['day'].strftime('%b %d'), "total": float(x['total'])} for x in sales_data]

        # --- Microservice Employee Count Logic ---
        employee_count = 0
        try:
            # Internal Docker request
            node_response = requests.get("http://employee_service:3000/employee", timeout=2)
            
            if node_response.status_code == 200:
                data = node_response.json()
                # LOGGING: See this in your terminal to verify data flow
                print(f"DEBUG: Successfully fetched from Node. Data: {data}")
                
                if isinstance(data, list):
                    employee_count = len(data)
                elif isinstance(data, dict):
                    employee_count = data.get('count', 0)
            else:
                print(f"DEBUG: Node API error status: {node_response.status_code}")
                employee_count = "Error"
        except Exception as e:
            print(f"DEBUG: Failed to connect to employee_service: {e}")
            employee_count = "Offline"

        extra_context = extra_context or {}
        extra_context.update({
            'total_revenue': total_revenue,
            'customer_count': customer_count,
            'employee_count': employee_count, # Verify this variable is used in admin/index.html
            'chart_data': json.dumps(chart_data),
            'top_products': OrderItem.objects.values('product__name').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:5],
            'low_stock_products': Product.objects.filter(stock_quantity__lt=5).order_by('stock_quantity'),
            'recent_payments': Payment.objects.select_related('order', 'order__customer').order_by('-created_at')[:5],
        })
        return super().index(request, extra_context)

mysite = MyAdminSite(name='myadmin')
mysite.index_template = 'admin/index.html'

# -------------------------------------------------------------------
# 3. Actions & Utility Views
# -------------------------------------------------------------------

def get_order_total(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        return JsonResponse({'total_due': float(order.total_due)})
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

@admin.action(description="Download PDF Invoice")
def download_invoice(modeladmin, request, queryset):
    order = queryset.first() 
    if not order: return HttpResponse("No order selected", status=400)
    
    payload = {
        "order_id": str(order.id),
        "customer_name": f"{order.customer.first_name} {order.customer.last_name}",
        "amount": float(order.total_due),
        "items": [{"name": i.product.name, "price": float(i.price_at_purchase)} for i in order.items.all()]
    }
    try:
        response = requests.post("http://invoice_service:8001/generate-invoice/", json=payload, timeout=5)
        if response.status_code == 200:
            django_response = HttpResponse(response.content, content_type='application/pdf')
            django_response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
            return django_response
    except Exception:
        return HttpResponse("Invoice Service Unavailable", status=503)

@admin.action(description="Export selected orders to CSV")
def export_orders_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Date', 'Status', 'Total Due'])
    for order in queryset:
        writer.writerow([order.id, str(order.customer), order.date_order.strftime("%Y-%m-%d %H:%M"), "Complete" if order.complete else "Pending", order.total_due])
    return response

# -------------------------------------------------------------------
# 4. Admins & Inlines
# -------------------------------------------------------------------

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['price_at_purchase']
    raw_id_fields = ['product']

@admin.register(Order, site=mysite)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'date_order', 'complete', 'total_due']
    inlines = [OrderItemInline]
    actions = [export_orders_to_csv, download_invoice]
    readonly_fields = ['total_due']
    class Media:
        js = ('js/admin_order_calc.js',)

@admin.register(Product, site=mysite)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_price', 'stock_quantity']
    list_editable = ['current_price', 'stock_quantity']

@admin.register(Payment, site=mysite)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'amount', 'method', 'status', 'created_at']

# -------------------------------------------------------------------
# 5. Final Registrations
# -------------------------------------------------------------------

mysite.register(EmployeeLink, EmployeeLinkAdmin)
mysite.register(InvoiceLink, InvoiceLinkAdmin)

class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [CustomerInline]

mysite.register(User, CustomUserAdmin)
mysite.register(Group, GroupAdmin)
mysite.register(Shipment, site=mysite)
mysite.register(Outbox, site=mysite)