"""Deterministic Employee Database Lookup Tool."""

from typing import Dict, Any

# Mock Enterprise Employee Records
EMPLOYEE_DIRECTORY: Dict[str, Dict[str, Any]] = {
    "EMP-101": {
        "name": "Sarah Chen",
        "role": "Senior Cloud Architect",
        "employment_type": "FTE",
        "country": "SG",
        "tenure_days": 730,  # 2 years
        "on_probation": False,
        "pto_balance_days": 14,
        "caregiver_role": "Primary Caregiver"
    },
    "EMP-202": {
        "name": "Marcus Tan",
        "role": "Customer Engineer",
        "employment_type": "FTE",
        "country": "SG",
        "tenure_days": 45,   # Probationary
        "on_probation": True,
        "pto_balance_days": 2,
        "caregiver_role": "Secondary Caregiver"
    },
    "EMP-303": {
        "name": "Alex Miller",
        "role": "Staff Augmentation Consultant",
        "employment_type": "VENDOR",
        "country": "SG",
        "tenure_days": 400,
        "on_probation": False,
        "pto_balance_days": 0,
        "caregiver_role": "Primary Caregiver"
    },
    "EMP-404": {
        "name": "Priya Sharma",
        "role": "Principal Solutions Architect",
        "employment_type": "FTE",
        "country": "SG",
        "tenure_days": 1825, # 5 years
        "on_probation": False,
        "pto_balance_days": 21,
        "caregiver_role": None
    }
}

def lookup_employee(employee_id: str) -> Dict[str, Any]:
    """
    Retrieves the verified corporate HR profile for a given employee_id (e.g. EMP-101).
    Returns employment type, country of tax domicile, tenure in days, probation status,
    and available PTO balances.
    """
    clean_id = employee_id.strip().upper()
    if clean_id in EMPLOYEE_DIRECTORY:
        record = EMPLOYEE_DIRECTORY[clean_id].copy()
        record["employee_id"] = clean_id
        return record
    return {
        "error": f"Employee '{clean_id}' was not found in corporate HR records.",
        "employee_id": clean_id
    }
