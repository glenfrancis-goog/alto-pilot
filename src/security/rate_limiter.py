"""Identity-Aware Rate Limiting (Agent Gateway CTA Ingress).

Strictly conforms to SDD Section 1.3, 4.3, and Table 5.6 (60 req/min per User ID).
"""

import threading
import time
from collections import defaultdict
from typing import Tuple, Dict

class IdentityRateLimiter:
    def __init__(self, limit_rpm: int = 60):
        self.limit_rpm = limit_rpm
        self.user_requests = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, user_id: str) -> Tuple[bool, int]:
        """Checks whether the user has exceeded their rolling 60-second limit.
        
        Returns:
            (is_allowed, retry_after_seconds)
        """
        now = time.time()
        window_start = now - 60.0

        with self.lock:
            # Purge timestamps older than 60s
            self.user_requests[user_id] = [t for t in self.user_requests[user_id] if t > window_start]

            if len(self.user_requests[user_id]) >= self.limit_rpm:
                earliest = self.user_requests[user_id][0]
                retry_after = max(1, int(60.0 - (now - earliest)))
                return False, retry_after

            self.user_requests[user_id].append(now)
            return True, 0
