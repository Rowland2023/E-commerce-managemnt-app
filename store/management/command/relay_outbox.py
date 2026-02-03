# store/management/commands/relay_outbox.py
import time
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from store.models import Outbox

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Relays pending Outbox events to the message broker"

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of events to process per batch"
        )
        parser.add_argument(
            "--interval",
            type=float,
            default=0.5,
            help="Polling interval in seconds"
        )

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        interval = options["interval"]

        self.stdout.write(self.style.SUCCESS("Starting Outbox Relayer..."))

        try:
            while True:
                with transaction.atomic():
                    events = (
                        Outbox.objects.filter(status="pending")
                        .select_for_update(skip_locked=True)[:batch_size]
                    )

                    if not events:
                        time.sleep(interval)
                        continue

                    for event in events:
                        try:
                            logger.info(f"Relaying event {event.id}: {event.event_type}")
                            # --- INTEGRATION POINT ---
                            # Example: broker.send(event.payload)
                            # --------------------------

                            event.status = "sent"
                            event.processed_at = timezone.now()
                            event.save()

                        except Exception as e:
                            event.status = "failed"
                            event.save()
                            logger.error(f"Failed to relay {event.id}: {str(e)}")

                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Outbox Relayer stopped gracefully."))
