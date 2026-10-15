"""
Unsubscribed Senders Store
--------------------------
Remembers which sender domains were unsubscribed so later scans can hide them.
Persisted as JSON next to token.json (i.e. /app/data in Docker).
"""

import json
import logging
import os
import threading
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# Senders often need a few days to process an unsubscribe. Mail newer than
# this after unsubscribing means it didn't work, so the sender is shown again.
GRACE_PERIOD = timedelta(days=7)

_lock = threading.Lock()


def _store_path() -> str:
    return os.path.join(
        os.path.dirname(os.path.abspath(settings.token_file)), "unsubscribed.json"
    )


def _load() -> dict:
    path = _store_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError) as e:
        logger.warning(f"Could not read {path}: {e}")
        return {}


def get_unsubscribed() -> dict:
    """Return {domain: {"unsubscribed_at": iso8601, "method": str}}."""
    with _lock:
        return _load()


def mark_unsubscribed(domain: str, method: str) -> None:
    """Record that a sender domain was unsubscribed (now)."""
    domain = (domain or "").strip().lower()
    if not domain:
        return
    with _lock:
        data = _load()
        data[domain] = {
            "unsubscribed_at": datetime.now(timezone.utc).isoformat(),
            "method": method,
        }
        path = _store_path()
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)
        os.replace(tmp, path)


def still_sending(last_date: Optional[str], unsubscribed_at: str) -> bool:
    """True if the newest email arrived after unsubscribing plus the grace period."""
    if not last_date:
        return False
    try:
        last = parsedate_to_datetime(last_date)
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return last > datetime.fromisoformat(unsubscribed_at) + GRACE_PERIOD
    except (ValueError, TypeError):
        return False
