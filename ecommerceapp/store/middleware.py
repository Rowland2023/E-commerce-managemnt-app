import logging
import json
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status

logger = logging.getLogger(__name__)

class IdempotencyMiddleware:
    """
    Middleware to enforce idempotency for state-changing requests (POST, PUT, PATCH).
    Uses an Idempotency-Key header to ensure duplicate requests return the same response.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Configurable TTLs via settings
        self.lock_ttl = getattr(settings, "IDEMPOTENCY_LOCK_TTL", 60)       # 1 minute lock
        self.response_ttl = getattr(settings, "IDEMPOTENCY_RESPONSE_TTL", 86400)  # 24 hours

    def __call__(self, request):
        # 1. Only apply to POST/PUT/PATCH (state-changing methods)
        if request.method not in ["POST", "PUT", "PATCH"]:
            return self.get_response(request)

        key = request.headers.get("Idempotency-Key")
        if not key:
            return self.get_response(request)

        lock_key = f"idemp_lock_{key}"
        resp_key = f"idemp_resp_{key}"

        # 2. Atomic lock check
        is_new_request = cache.add(lock_key, "LOCKED", timeout=self.lock_ttl)

        if not is_new_request:
            cached_data = cache.get(resp_key)
            if cached_data:
                logger.info(f"Idempotency hit for key={key}")
                return JsonResponse(cached_data, status=status.HTTP_200_OK)

            # If locked but no response yet, request is still in flight
            logger.warning(f"Duplicate request in flight for key={key}")
            return JsonResponse(
                {"error": "Request already in progress. Please wait."},
                status=status.HTTP_409_CONFLICT
            )

        # 3. Process the request
        try:
            response = self.get_response(request)

            # 4. Cache successful or client-error responses (<500)
            if response.status_code < 500:
                try:
                    if hasattr(response, "data"):
                        response_data = response.data
                    else:
                        # Fallback for non-DRF responses
                        try:
                            response_data = json.loads(response.content.decode("utf-8"))
                        except Exception:
                            response_data = {"raw": response.content.decode("utf-8")}
                    cache.set(resp_key, response_data, timeout=self.response_ttl)
                    logger.info(f"Cached idempotent response for key={key}")
                except Exception as e:
                    logger.error(f"Failed to cache response for key={key}: {e}")

            return response
        finally:
            # Clean up the lock, keep the cached response
            cache.delete(lock_key)
