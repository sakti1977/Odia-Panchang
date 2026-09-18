"""
Minimal retry helper for transient failures.

Only wrap operations that are safe to repeat:
  - Graph API reads (page info, recent posts, photo CDN URL, container status)
  - Hosting a JPEG on a temporary public URL so Instagram can fetch it
Do NOT wrap Facebook /photos|/feed or Instagram /media_publish — those are
not idempotent. Duplicate-post prevention lives in the daily workflow
(date-keyed cache) plus a recent-caption fingerprint in meta_poster.
"""

from __future__ import annotations

import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def retry(*, attempts=3, base_delay_seconds=1.0, exceptions=(Exception,)):
    """Retry on the given exception types with exponential backoff."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt == attempts:
                        break
                    delay = base_delay_seconds * (2 ** (attempt - 1))
                    logger.warning(
                        "%s failed (attempt %d/%d): %r — retrying in %.1fs",
                        func.__name__,
                        attempt,
                        attempts,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator
