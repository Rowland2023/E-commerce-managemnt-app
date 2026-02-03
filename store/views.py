from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from store.models import Customer, Product, Order, OrderItem, Payment, Shipment, Outbox
from store.serializers import (
    CustomerSerializer,
    ProductSerializer,
    OrderSerializer,
    OrderItemSerializer,
    PaymentSerializer,
    ShipmentSerializer,
    OutboxSerializer,
)


# 1. Customer ViewSet
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "email", "phone_number"]
    filterset_fields = ["email"]


# 2. Product ViewSet (Search + Filter)
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ["name", "description"]
    filterset_fields = ["stock_quantity"]
    ordering_fields = ["current_price", "stock_quantity"]
    ordering = ["name"]


# 3. Order ViewSet (Deep Prefetch + Ordering)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related("customer").prefetch_related("items__product")
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["complete", "transaction_id"]
    ordering_fields = ["date_order", "total_due"]
    ordering = ["-date_order"]


# 4. OrderItem ViewSet
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all().select_related("order", "product")
    serializer_class = OrderItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["order", "product"]


# 5. Payment ViewSet
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().select_related("order")
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "method"]
    ordering_fields = ["amount", "created_at"]
    ordering = ["-created_at"]


# 6. Shipment ViewSet
class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all().select_related("order")
    serializer_class = ShipmentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status"]
    ordering_fields = ["shipped_at"]
    ordering = ["-shipped_at"]


# 7. Outbox ViewSet (Audit-only, ReadOnly)
class OutboxViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Outbox.objects.all().order_by("-created_at")
    serializer_class = OutboxSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "event_type"]
