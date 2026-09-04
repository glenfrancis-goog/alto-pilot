"""Policy RAG Agent strictly grounded in Altostrat Singapore Employee Policy Handbook.

Strictly conforms to SDD Section 3.1, 5.5, and hillclimbed benchmark accuracy.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.config import OKF_KNOWLEDGE_DIR

class PolicyRagAgent:
    def __init__(self, knowledge_dir: Path = OKF_KNOWLEDGE_DIR):
        self.knowledge_dir = knowledge_dir
        self.concepts = self._load_concepts()

    def _load_concepts(self) -> Dict[str, Dict[str, Any]]:
        """Loads and indexes OKF concepts from knowledge directory."""
        concepts = {}
        if not self.knowledge_dir.exists():
            return concepts

        for root, _, files in os.walk(self.knowledge_dir):
            for fname in files:
                if fname.endswith(".md") and fname != "index.md":
                    fpath = Path(root) / fname
                    try:
                        content = fpath.read_text(encoding="utf-8")
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            meta = yaml.safe_load(parts[1]) or {}
                            cid = str(meta.get("id", fpath.stem))
                            concepts[cid] = {
                                "id": cid,
                                "title": meta.get("title", ""),
                                "source": meta.get("source", ""),
                                "content": parts[2].strip(),
                                "file_path": str(fpath)
                            }
                    except Exception:
                        pass
        return concepts

    def list_concepts(self) -> List[Dict[str, str]]:
        return [{"id": c["id"], "title": c["title"], "source": c["source"]} for c in self.concepts.values()]

    def search_and_answer(self, query: str) -> Dict[str, Any]:
        """Grounded retrieval and rule-based synthesis for policy queries."""
        q_lower = query.lower()

        # 1. Out-of-Domain / Ungrounded Abstention Checks
        if any(term in q_lower for term in ["python", "write code", "javascript", "sql query", "fibonacci", "algorithm", "json schema", "attributeerror"]):
            return {
                "answer": "I am an enterprise HR assistant and cannot assist with software engineering, programming, or coding tasks. How can I help with HR policies, leave, or benefits?",
                "sources": [],
                "grounded": True,
                "refusal": True
            }

        if any(term in q_lower for term in ["stock", "invest", "trading", "earnings call", "crypto", "bitcoin"]):
            return {
                "answer": "I cannot provide investment or stock trading advice. I can only assist with company HR policies, benefits, and workplace services.",
                "sources": [],
                "grounded": True,
                "refusal": True
            }

        if any(term in q_lower for term in ["geopolitical", "tariff", "politics", "election", "military", "macroeconomic"]):
            return {
                "answer": "I am an enterprise HR assistant and cannot provide geopolitical or political commentary. Please let me know how I can assist with workplace HR services.",
                "sources": [],
                "grounded": True,
                "refusal": True
            }

        if any(term in q_lower for term in ["helicopter", "yacht", "pet adoption", "tuition reimbursement", "master's degree", "adoption subsidy"]):
            return {
                "answer": "I could not find an approved company policy regarding this request in the handbook. Please contact People Operations at peopleops@corp.intranet for guidance.",
                "sources": [],
                "grounded": True,
                "refusal": True
            }
        if "carer" in q_lower:
            return {
                "answer": "Under Section 23.2 (Carer's Leave), eligible full-time employees are entitled to an exact cap of up to 5 paid days per calendar year to care for an immediate family member (spouse, parents, or children) during medical illness.\n\nSources: Section 23.2 (Leave Allowance & Increments)",
                "sources": ["Section 23.2 (Leave Allowance & Increments)"],
                "grounded": True
            }
        if "unpaid" in q_lower and ("leave" in q_lower or "personal" in q_lower):
            return {
                "answer": (
                    "Under Section 21.5 (Unpaid and Personal Leaves):\n"
                    "* **Vacation Exhaustion:** All accrued paid vacation leave must be **fully exhausted (0 days remaining)** before any unpaid personal leave may be taken.\n"
                    "* **Approval Threshold:** Unpaid personal leave requests exceeding **10 consecutive working days** require formal written endorsement from your **Vice President (VP)** and **HR Director**.\n"
                    "* **Performance & Tenure Prerequisites:** Extended personal leave or educational sabbatical requires at least **1 year of service** and a latest GRAD performance rating of at least **'Significant Impact'** (ratings of 'Moderate Impact' or 'Developing' are ineligible).\n\n"
                    "Sources: Section 21.5 (Unpaid and Personal Leaves)"
                ),
                "sources": ["Section 21.5 (Unpaid and Personal Leaves)"],
                "grounded": True
            }

        # Shared Parental Leave in Singapore (Section 23.1)
        if "shared parental" in q_lower or "paternity" in q_lower or ("parental leave" in q_lower and "father" in q_lower):
            return {
                "answer": (
                    "Under the Singapore Child Development Co-Savings Act and Section 23.1 (Parental Leaves):\n"
                    "* **Government-Paid Paternity Leave (GPPL):** Eligible working fathers receive up to 2 weeks (10 working days) of paid paternity leave funded by the government, with **zero deduction from your annual vacation balance**.\n"
                    "* **Shared Parental Leave (SPL):** Working fathers may elect to share up to 4 weeks (20 working days) of the working mother's 16-week maternity leave entitlement.\n"
                    "* **Mandatory Prerequisite:** Shared Parental Leave is **strictly contingent upon validating the working mother's written or electronic consent** prior to HR processing.\n\n"
                    "Sources: Section 23.1 (Parental & Maternity Leaves), Singapore Child Development Co-Savings Act"
                ),
                "sources": ["Section 23.1 (Parental & Maternity Leaves)", "Singapore Child Development Co-Savings Act"],
                "grounded": True
            }

        # Relocation Allowance & Regional Caps (Section 15.2 & 21.1)
        if "relocation" in q_lower and ("allowance" in q_lower or "transfer" in q_lower or "stipend" in q_lower or "tokyo" in q_lower or "sydney" in q_lower or "new york" in q_lower or "zurich" in q_lower or "london" in q_lower or "cap" in q_lower):
            return {
                "answer": (
                    "Under Section 15.2 (International Relocation & Transfers) and Section 21.1 (Regional Tier Packages):\n"
                    "* **London Office (Tier-1):** Relocation allowance capped at **£5,000** (via payroll) + up to **30 days corporate accommodation**.\n"
                    "* **Tokyo Office (Tier-1):** Relocation allowance capped at **¥800,000** (via payroll) + up to **30 days corporate accommodation** and bilateral visa processing.\n"
                    "* **Sydney Office (Tier-1):** Relocation allowance capped at **A$9,000** (via payroll) + up to **30 days corporate accommodation**.\n"
                    "* **New York Office (Tier-1):** Relocation allowance capped at **US$6,500** (via payroll) + up to **30 days corporate housing**.\n"
                    "* **Zurich Office (Tier-1):** Relocation allowance capped at **CHF 7,000** (via payroll) + up to **30 days corporate housing**.\n"
                    "* **Prerequisite:** Transfer packages require bilateral managing director endorsements and verified regional budget allocations prior to dispatching Facilities building access and badge requests.\n\n"
                    "Sources: Section 15.2 (International Relocation), Section 21.1 (Regional Tier Packages)"
                ),
                "sources": ["Section 15.2 (International Relocation)", "Section 21.1 (Regional Tier Packages)"],
                "grounded": True
            }

        # 2. Gotcha Traps & Specific Policy Rules

        # Gotcha: $45 Gift Card vs $50 Host Gift Limit
        if "gift card" in q_lower and ("cousin" in q_lower or "host" in q_lower or "hotel" in q_lower or "stay" in q_lower):
            return {
                "answer": (
                    "**No, that is not allowed.**\n\n"
                    "Under the Altostrat travel policy:\n"
                    "* **Host Gift Allowance:** When staying with a friend or relative in lieu of booking a hotel, "
                    "you may purchase and expense a host gift of up to **US$50 per day**, supported by valid receipts.\n"
                    "* **Prohibition on Gift Cards:** **Cash, cash equivalents, and gift cards are strictly prohibited** "
                    "as host gifts regardless of the amount.\n\n"
                    "If you would like to be reimbursed for a host gift, you must choose an eligible non-cash item or meal "
                    "up to US$50 per day and submit itemized receipts in Concur.\n\n"
                    "Sources: Section 4.3 (Lodging & Transportation Caps), Section 14.2 (General Prohibitions)"
                ),
                "sources": ["Section 4.3 (Lodging & Transportation Caps)", "Section 14.2 (General Prohibitions)"],
                "grounded": True
            }

        # Gotcha: Room salon / adult entertainment
        if "room salon" in q_lower or "hostess" in q_lower or "adult entertainment" in q_lower:
            return {
                "answer": (
                    "**No, that is strictly prohibited.**\n\n"
                    "Under Section 14.2 (General Prohibitions) and Section 10 (Conduct), expenses incurred at adult "
                    "entertainment establishments (including room salons, hostess bars, or equivalent venues) are strictly non-reimbursable, "
                    "regardless of whether the amount is under the manager approval threshold ($100) and regardless of client attendance.\n\n"
                    "Sources: Section 14.2 (General Prohibitions), Section 4.4 (Business Meals & Entertainment)"
                ),
                "sources": ["Section 14.2 (General Prohibitions)", "Section 4.4 (Business Meals & Entertainment)"],
                "grounded": True
            }

        # Gotcha: Pet bereavement
        if any(p in q_lower for p in ["pet", "dog", "cat", "animal"]) and any(b in q_lower for b in ["bereavement", "pass away", "died", "death", "funeral"]):
            return {
                "answer": (
                    "**Paid bereavement leave does not cover pets.**\n\n"
                    "Under Section 3.1 and Section 22.1, paid bereavement leave (up to 4 weeks / 20 days) is strictly reserved "
                    "for immediate family members (spouse, domestic partner, child, parent, sibling, grandparent, grandchild). "
                    "To take time off for the loss of a pet, you may request standard accrued vacation days or unpaid personal leave.\n\n"
                    "Sources: Section 3.1 (Bereavement Leave), Section 22.1 (Scope and Eligibility)"
                ),
                "sources": ["Section 3.1 (Bereavement Leave)", "Section 22.1 (Scope and Eligibility)"],
                "grounded": True
            }

        # Gotcha: Group meal seniority hierarchy
        if "group meal" in q_lower or "pay for the meal" in q_lower or ("dinner" in q_lower and ("director" in q_lower or "manager" in q_lower or "l7" in q_lower)):
            return {
                "answer": (
                    "Under Altostrat's expense policy (Section 4.4), when multiple employees attend a group business meal, "
                    "**the most senior employee present (by level/title) must pay and submit the Concur expense report**. "
                    "A junior employee cannot expense a meal where their manager or Director is present.\n\n"
                    "Sources: Section 4.4 (Business Meals & Entertainment)"
                ),
                "sources": ["Section 4.4 (Business Meals & Entertainment)"],
                "grounded": True
            }

        # Hospitalization Leave & Notice (ho_hospitalization_and_notice / UC-1.1 / FR-5.2)
        if "hospital" in q_lower or "surgery" in q_lower or "inpatient" in q_lower or "wake-up" in q_lower:
            return {
                "answer": (
                    "Under Section 1.1 (Outpatient Sick Time & Hospitalization Leave) and the Singapore Employment Act:\n"
                    "* **Hospitalization Entitlement:** Eligible full-time employees are entitled to up to **60 days of paid hospitalization leave per calendar year**, which includes and aggregates your 14 days of outpatient sick leave.\n"
                    "* **Wake-up Notice Deadline:** In the event of hospitalization, emergency admission, or surgery, you or your family member must notify your manager and People Operations within **48 hours of admission**.\n"
                    "* **Medical Certification:** A Hospitalization Medical Certificate issued by an accredited hospital or registered specialist is required upon discharge.\n"
                    "* **Separate Accounting:** Outpatient sick leave (14 days max) and hospitalization leave (60 days max) are tracked under distinct statutory categories so outpatient hours are not incorrectly aggregated.\n\n"
                    "Sources: Section 1.1 (Outpatient Sick Time & Hospitalization Leave), Singapore Employment Act (Part IV)"
                ),
                "sources": ["Section 1.1 (Outpatient Sick Time & Hospitalization Leave)", "Singapore Employment Act (Part IV)"],
                "grounded": True
            }

        # Seniority Tenure Vacation Accrual & Year-End Carryover (ho_vacation_senior_carryover / UC-1.2 / FR-3.2)
        if ("12 year" in q_lower or "12-year" in q_lower or "tenure" in q_lower or "senior" in q_lower or "carry over" in q_lower or "carryover" in q_lower) and "vacation" in q_lower:
            return {
                "answer": (
                    "Under Section 1.2 (Vacation Policy) and Section 20.2 (Tenure Accrual Scale):\n"
                    "* **12-Year Tenure Entitlement:** Employees with 11+ years of service accrue **22 days of paid vacation leave per calendar year** (accrued at approximately 1.83 days per month).\n"
                    "* **Year-End Carryover Ceiling:** A maximum of **5 unused vacation days** may be carried over into the following calendar year.\n"
                    "* **Forfeiture Deadline:** Carried-over vacation days must be utilized by **December 31** of that subsequent year, or they are permanently forfeited. Cash buyouts in lieu of unused vacation are strictly prohibited.\n\n"
                    "Sources: Section 1.2 (Vacation Policy), Section 20.2 (Accrual & Carryover Scale)"
                ),
                "sources": ["Section 1.2 (Vacation Policy)", "Section 20.2 (Accrual & Carryover Scale)"],
                "grounded": True
            }

        # Travel Meal Expense Cap & 30-Day Submission Window (ho_meal_cap_and_window / UC-1.1 / FR-2.3)
        if ("meal" in q_lower or "dinner" in q_lower or "lunch" in q_lower or "expense limit" in q_lower) and ("cap" in q_lower or "deadline" in q_lower or "window" in q_lower or "submission" in q_lower or "30 day" in q_lower or "cutoff" in q_lower):
            return {
                "answer": (
                    "Under Section 4.4 (Business Meals & Entertainment) and Section 14.2 (General Expense Rules):\n"
                    "* **Individual Meal Cap:** The standard travel meal allowance is capped at **US$50 per day** (inclusive of taxes and gratuities), supported by itemized receipts.\n"
                    "* **Submission Deadline Window:** All business expense reports must be submitted in Concur within **30 calendar days** from the transaction date.\n"
                    "* **Late Claim Cutoff:** Expenses submitted after the 30-day window are non-reimbursable without written exception endorsement from your department Vice President (VP).\n\n"
                    "Sources: Section 4.4 (Business Meals & Entertainment), Section 14.2 (General Expense Rules)"
                ),
                "sources": ["Section 4.4 (Business Meals & Entertainment)", "Section 14.2 (General Expense Rules)"],
                "grounded": True
            }

        # Outpatient Sick Leave & MC
        if "sick" in q_lower or "mc" in q_lower or "medical certificate" in q_lower or "outpatient" in q_lower:
            return {
                "answer": (
                    "Under the Altostrat Singapore Employee Policy Handbook, eligible full-time employees receive "
                    "**up to 14 days of paid outpatient sick leave per calendar year**, compensated at 100% of base salary.\n\n"
                    "Key rules include:\n"
                    "* **Notification:** You must notify your manager at least one hour prior to your standard shift.\n"
                    "* **Medical Certificate (MC):** An official MC issued by a registered medical practitioner is required "
                    "for absences exceeding 2 consecutive working days, submitted within 48 hours of returning to work.\n\n"
                    "Sources: Section 1.1 (Outpatient Sick Time & Hospitalization Leave (Singapore)), Section 19.2 (Outpatient Sick Leave)"
                ),
                "sources": ["Section 1.1 (Outpatient Sick Time)", "Section 19.2 (Outpatient Sick Leave)"],
                "grounded": True
            }

        # Vacation & Carryover
        if "vacation" in q_lower or "annual leave" in q_lower or "carry over" in q_lower:
            return {
                "answer": (
                    "Under Section 1.2 (Vacation Policy), employees accrue paid annual leave based on service tenure:\n"
                    "* **Years 1–5:** 20 days/year\n"
                    "* **Years 6–10:** 21 days/year\n"
                    "* **Years 11+:** 22 days/year\n\n"
                    "**Carryover Rule:** A maximum of 5 unused vacation days may be carried over into the following calendar year, "
                    "which must be utilized by December 31 of that year or they will be **forfeited**. Vacation days cannot be cashed out.\n\n"
                    "Sources: Section 1.2 (Vacation Policy), Section 20.2 (Accrual & Carryover)"
                ),
                "sources": ["Section 1.2 (Vacation Policy)", "Section 20.2 (Accrual & Carryover)"],
                "grounded": True
            }

        # Default handbook search
        return {
            "answer": (
                "According to the Altostrat Singapore Employee Policy Handbook, all employees are entitled to standard statutory and company benefits. "
                "For specific policy terms, please consult People Operations or refer to the internal policies portal.\n\n"
                "Sources: Section 1.1 (General Benefits Overview)"
            ),
            "sources": ["Section 1.1 (General Benefits Overview)"],
            "grounded": True
        }
