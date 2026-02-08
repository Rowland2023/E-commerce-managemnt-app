import time
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from store.models import Outbox

class Command(BaseCommand):
    help = "Polls the Outbox table and sends pending events to microservices."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Outbox Relay Service Started..."))
        
        while True:
            # Fetch all pending or failed events
            pending_events = Outbox.objects.filter(status__in=["pending", "failed"]).order_by('created_at')

            for event in pending_events:
                self.stdout.write(f"📦 Processing Event {event.id}: {event.event_type}")
                
                try:
                    # Logic for Invoice Generation
                    if event.event_type == 'GENERATE_INVOICE':
                        response = requests.post(
                            "http://invoice_service:8001/generate-invoice/", 
                            json=event.payload, 
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            event.status = "sent"
                            event.processed_at = timezone.now()
                            event.save()
                            self.stdout.write(self.style.SUCCESS(f"✅ Successfully sent Event {event.id}"))
                        else:
                            raise Exception(f"Service returned {response.status_code}")

                except Exception as e:
                    event.status = "failed"
                    event.save()
                    self.stdout.write(self.style.ERROR(f"❌ Failed to send Event {event.id}: {e}"))

            # Sleep for 10 seconds before checking again
            time.sleep(10)