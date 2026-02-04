from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers
from store.models import Customer, Product, Order, OrderItem, Outbox, Shipment, Payment


# --- Customer Serializer ---
class CustomerSerializer(serializers.ModelSerializer):
    # Change from SlugRelatedField to PrimaryKeyRelatedField
    user = serializers.PrimaryKeyRelatedField( 
        queryset=User.objects.all(), 
        style={'base_template': 'input.html'} # Keeps it as a text box instead of a dropdown
    )

    class Meta:
        model = Customer
        fields = ["id", "user", "first_name", "last_name", "email", "phone_number"]

# --- Product Serializer ---
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


# --- Payment Serializer ---
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


# --- Shipment Serializer ---
class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = "__all__"


# --- Outbox Serializer ---
class OutboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outbox
        fields = "__all__"


# --- Order Item Serializer ---
class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product"
    )
    product = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product_id", "product", "quantity", "price_at_purchase"]
        read_only_fields = ["price_at_purchase"]


# --- Order Serializer ---
class OrderSerializer(serializers.HyperlinkedModelSerializer):
    # Make customer writable, not read-only
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["url", "id", "customer", "items", "total_due", "transaction_id", "complete"]

    # --- STOCK CHECK VALIDATION ---
    def validate(self, data):
        items_data = data.get("items")
        if not items_data:
            raise serializers.ValidationError({"items": "Order must contain at least one item."})

        for item in items_data:
            product = item["product"]
            requested_quantity = item["quantity"]

            if product.stock_quantity < requested_quantity:
                raise serializers.ValidationError({
                    "items": f"Not enough stock for {product.name}. "
                             f"Requested: {requested_quantity}, Available: {product.stock_quantity}"
                })
        return data

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        with transaction.atomic():
            # 1. Create the Order
            order = Order.objects.create(**validated_data)

            total_due = 0

            # 2. Process items and decrement stock
            for item_data in items_data:
                product = Product.objects.select_for_update().get(pk=item_data["product"].pk)
                quantity = item_data["quantity"]

                # Create the line item
                line_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=product.current_price,
                )

                # Update the inventory safely
                product.stock_quantity -= quantity
                product.save()

                # Update total due
                total_due += line_item.quantity * line_item.price_at_purchase

            # 3. Update order total
            order.total_due = total_due
            order.save()

            # 4. Log the Outbox Event
            Outbox.objects.create(
                event_type="ORDER_PLACED",
                payload={
                    "order_id": order.id,
                    "total_due": str(order.total_due),
                    "customer_email": order.customer.email if order.customer else None,
                },
            )

        return order
