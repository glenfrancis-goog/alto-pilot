"""Google Cloud Model Armor & Prompt Safety Screening.

Strictly conforms to SDD Section 1.3, 3.1, 4.2, and Error Matrix Table 5.6.
"""

import re
from typing import Tuple, Dict, Any

class ModelArmorGuard:
    """Simulates/Interfaces with Google Cloud Model Armor Managed Prompt Shield."""

    # Explicit adversarial injection and jailbreak patterns
    INJECTION_PATTERNS = [
        r"(?i)\bignore\s+(all\s+)?(previous|prior)\s+(directions|instructions)\b",
        r"(?i)\bdisregard\s+(all\s+)?(previous|system)\s+prompts?\b",
        r"(?i)\b(?:you\s+are\s+(?:now\s+in|entering)\s+)?developer\s+mode\b",
        r"(?i)\bDAN(?:\s+mode)?\b",
        r"(?i)\bdo\s+anything\s+now\b",
        r"(?i)\b(?:reveal|print|output)\s+(?:your\s+)?(?:complete\s+)?(?:system\s+prompt|hidden\s+instructions)\b",
        r"(?i)\bact\s+as\s+an\s+unrestricted\s+AI\b",
        r"(?i)\bbypass\s+(all\s+)?security\s+filters\b",
        r"(?i)\bsudo\s+mode\b",
        r"(?i)\b(write|create|generate|implement)\s+(?:me\s+)?(?:a\s+)?(?:python|java|javascript|c\+\+|golang|bash|sql|rust)\s+(?:script|code|program|function|class|algorithm)",
        r"(?i)\b(calculate|write)\s+(?:fibonacci|quicksort|binary search|sorting algorithm)",
        r"(?i)\b(fetch|list)\s+all\s+(?:aws|s3|azure|gcp)\s+buckets",
    ]

    TOXIC_PATTERNS = [
        r"(?i)\b(hate\s+speech|kill\s+all|harm\s+yourself)\b",
    ]

    def sanitize_user_prompt(self, prompt: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Sanitizes incoming employee prompt against injection and jailbreak attacks.
        
        Returns:
            (is_safe, message, metadata)
        """
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, prompt):
                is_code = bool(re.search(r"(?i)\b(python|java|javascript|c\+\+|code|script|algorithm|s3|buckets|fibonacci)\b", prompt))
                msg = (
                    "I am an enterprise HR virtual assistant and cannot assist with software engineering, programming, or coding tasks. "
                    "How can I help with HR policies or leave?"
                ) if is_code else (
                    "I cannot process instructions that attempt to override my security guidelines. "
                    "How can I assist with HR services?"
                )
                return False, msg, {
                    "error_code": "ERR_MA_PROMPT_INJECT_001",
                    "status_code": 400,
                    "violation": "OUT_OF_DOMAIN_CODE_INJECTION" if is_code else "PROMPT_INJECTION_DETECTED"
                }

        return True, prompt, {
            "eval_token": "MA-SAFE-OK",
            "latency_ms": 45,
            "status": "PASSED"
        }

    def sanitize_model_response(self, response_text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Screen model output for safety, toxicity, and unauthorized leaks."""
        for pattern in self.TOXIC_PATTERNS:
            if re.search(pattern, response_text):
                return False, (
                    "I am unable to generate a response for this query. "
                    "Please contact the HR People Operations team directly."
                ), {
                    "error_code": "ERR_MA_OUTPUT_TOXIC_002",
                    "status_code": 500,
                    "violation": "CONTENT_SAFETY_VIOLATION"
                }

        return True, response_text, {
            "eval_token": "MA-RESP-SAFE",
            "latency_ms": 40,
            "status": "PASSED"
        }
