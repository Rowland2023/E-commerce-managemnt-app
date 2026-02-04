# store/urls.py
from django.urls import path, include
from rest_framework import routers
from store.views import (
    CustomerViewSet,
    ProductViewSet,
    OrderViewSet,
    OrderItemViewSet,
    PaymentViewSet,
    ShipmentViewSet,
    OutboxViewSet,
)

# Create a router and register our viewsets
router = routers.DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'orderitems', OrderItemViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'shipments', ShipmentViewSet)
router.register(r'outbox', OutboxViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
