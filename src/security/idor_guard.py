"""Insecure Direct Object Reference (IDOR) Protection.

Strictly conforms to SDD Table 5.6 (ERR_AUTH_IDOR_TAMPER_005).
"""

from typing import Tuple

class IdorGuard:
    @staticmethod
    def validate_access(authenticated_user_id: str, target_employee_id: str) -> Tuple[bool, str]:
        """Validates that an employee only accesses or modifies their own records."""
        if not authenticated_user_id or not target_employee_id:
            return False, "Missing user context or employee ID."

        if authenticated_user_id != target_employee_id:
            return False, "You are only authorized to access your own employee profile and records."

        return True, "Authorized"
