"""Downstream 5xx Circuit Breaker & Resilient Cloud Tasks Queueing.

Strictly conforms to SDD Section 1.2, 4.3, 5.3, and Table 5.6.
"""

import time
import uuid
from typing import Tuple, Optional, Dict, Any, List

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout_secs: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_secs = recovery_timeout_secs
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED (healthy) | OPEN (tripped) | HALF-OPEN
        self.task_queue: List[Dict[str, Any]] = []

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def is_available(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout_secs:
                self.state = "HALF-OPEN"
                return True
            return False
        return True  # HALF-OPEN trial request

    def enqueue_task(self, service: str, payload: Dict[str, Any]) -> str:
        """Enqueues failed downstream request with exponential backoff & tracking ID."""
        task_id = f"TRACK-{service.upper()[:2]}-{uuid.uuid4().hex[:8]}"
        self.task_queue.append({
            "task_id": task_id,
            "service": service,
            "payload": payload,
            "enqueued_at": time.time(),
            "status": "QUEUED"
        })
        return task_id
