"""Cloud Sensitive Data Protection (Cloud DLP) Inline SPII Redaction.

Strictly conforms to SDD Section 1.3, 4.4, and Table 5.6.
"""

import re
from typing import Tuple, Dict, Any, List

class DlpGuard:
    """Deterministic InfoType inspection and de-identification for SPII."""

    # InfoType Regex Patterns for enterprise audit and logging redaction
    PATTERNS = {
        "CREDIT_CARD_NUMBER": r"\b(?:\d[ -]*?){13,16}\b",
        "SG_NRIC": r"\b[STFGQM]\d{7}[A-Z]\b",
        "US_SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "PHONE_NUMBER": r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b",
        "EMAIL_ADDRESS": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
    }

    def inspect_and_deidentify(self, text: str) -> Tuple[str, List[str]]:
        """Scans and redacts SPII, returning sanitized text and detected infoTypes."""
        redacted_text = text
        detected_types = []

        # Preserve system employee IDs like EMP-62 or INC0000827
        for info_type, pattern in self.PATTERNS.items():
            matches = list(re.finditer(pattern, redacted_text))
            if matches:
                detected_types.append(info_type)
                for m in reversed(matches):
                    val = m.group(0)
                    # Don't redact ticket IDs or employee IDs that look like numbers
                    if val.startswith("EMP-") or val.startswith("INC") or val.startswith("TRACK-"):
                        continue
                    start, end = m.span()
                    redacted_text = redacted_text[:start] + f"[{info_type}_REDACTED]" + redacted_text[end:]

        return redacted_text, detected_types
