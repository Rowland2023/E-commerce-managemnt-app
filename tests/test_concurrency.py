import threading
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Product, Customer

class TestConcurrencyAndIdempotencyTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(
            first_name="Test", last_name="User", email="test@example.com"
        )
        self.product = Product.objects.create(
            name="Limited Edition Item",
            stock_quantity=1,  # Only one left!
            current_price=100.00
        )
        self.url = reverse('order-list')

    def test_idempotency_blocks_duplicates(self):
        """Verify that the same Idempotency-Key returns the cached response."""
        order_data = {
            "transaction_id": "unique-tx-123",
            "items": [{"product_id": self.product.id, "quantity": 1}]
        }
        headers = {'HTTP_IDEMPOTENCY_KEY': 'stable-key-1'}

        # First request
        resp1 = self.client.post(self.url, order_data, format='json', **headers)
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        # Second request (Immediate duplicate)
        resp2 = self.client.post(self.url, order_data, format='json', **headers)
        
        # Should return 200 (cached) instead of creating a new order or failing
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        # Verify only one order was actually created in DB
        from store.models import Order
        self.assertEqual(Order.objects.count(), 1)

    def test_race_condition_prevented(self):
        """Simulate two users buying the last item at the exact same time."""
        
        def place_order():
            # Use a fresh client for each thread
            client = APIClient()
            data = {
                "transaction_id": f"tx-{threading.get_ident()}",
                "items": [{"product_id": self.product.id, "quantity": 1}]
            }
            # Each thread uses a DIFFERENT idempotency key to test stock locking
            headers = {'HTTP_IDEMPOTENCY_KEY': f'key-{threading.get_ident()}'}
            return client.post(self.url, data, format='json', **headers)

        # Create two threads
        thread1_resp = []
        thread2_resp = []

        t1 = threading.Thread(target=lambda: thread1_resp.append(place_order()))
        t2 = threading.Thread(target=lambda: thread2_resp.append(place_order()))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # One should succeed (201), one should fail (400 - Out of Stock)
        statuses = [thread1_resp[0].status_code, thread2_resp[0].status_code]
        
        self.assertIn(status.HTTP_201_CREATED, statuses)
        self.assertIn(status.HTTP_400_BAD_REQUEST, statuses)
        
        # Final safety check: stock should NOT be negative
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 0)