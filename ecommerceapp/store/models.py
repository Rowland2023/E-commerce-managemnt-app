from django.db import models
from django.conf import settings

# --- 1. EXTERNAL SERVICE LINK MODELS (Proxy/Dummy) ---
# These do not create tables but allow links in the Admin sidebar.
class EmployeeLink(models.Model):
    class Meta:
        managed = False  # No database table created
        verbose_name = "Employee Management"
        verbose_name_plural = "Employee Management"

class InvoiceLink(models.Model):
    class Meta:
        managed = False # No database table created
        verbose_name = "Invoice System"
        verbose_name_plural = "Invoice System"


# --- 2. CUSTOMER & PRODUCT CORE ---
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


# --- 3. ORDERING LOGIC ---
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    date_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    total_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def update_total_due(self):
        total = sum(item.get_total() for item in self.items.all())
        self.total_due = total
        self.save(update_fields=["total_due"])

    def __str__(self):
        return f"Order {self.id} - {self.customer}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.price_at_purchase:
            self.price_at_purchase = self.product.current_price
        super().save(*args, **kwargs)
        # Recalculate parent order total
        self.order.update_total_due()

    def get_total(self):
        return self.price_at_purchase * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# --- 4. FULFILLMENT & PAYMENTS ---
class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50) 
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - Order {self.order.id} ({self.status})"

class Shipment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="shipments")
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")
    shipped_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Shipment {self.id} - Order {self.order.id} ({self.status})"


# --- 5. MICROSERVICES OUTBOX ---
class Outbox(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    ]

    id = models.BigAutoField(primary_key=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"Outbox Event {self.id} - {self.event_type} ({self.status})"