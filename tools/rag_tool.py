"""Track A — RAG retrieval tool (Vertex AI Search)."""

from google.api_core.client_options import ClientOptions
from agent import config

try:
    from google.cloud import discoveryengine_v1 as discoveryengine
except ImportError:
    discoveryengine = None

MOCK_DATABASE = {
    "sick": {
        "title": "Handbook Section 1.1 — Outpatient Sick & Hospitalization Leave",
        "snippet": "Eligible employees receive up to 14 days of paid outpatient sick leave per calendar year at 100% of base salary, plus an additional 46 work days of hospitalization leave. If you are sick for more than two work days, submit an MC via WorkWeek within 48 hours.",
        "link": "https://hr-portal.altostrat.com/handbook#1.1-sick-hospitalization-leave"
    },
    "vacation": {
        "title": "Handbook Section 1.2 — Paid Vacation Leave",
        "snippet": "Accrual tiers: 1-6 years = 20 days, 7-10 years = 21 days, 11+ years = 22 days. Shift workers book by actual shift hours; a vacation day is an 8-hour block, so a 12-hour shift requires 1.5 vacation days.",
        "link": "https://hr-portal.altostrat.com/handbook#1.2-vacation-leave"
    },
    "ramp": {
        "title": "Handbook Section 2.3 — Ramp-Back Time",
        "snippet": "After at least 10 consecutive weeks of parental/baby-bonding leave, take up to 2 weeks of paid ramp-back time, working a minimum of 50% of normal weekly hours while receiving 100% of normal salary.",
        "link": "https://hr-portal.altostrat.com/handbook#2.3-ramp-back-time"
    },
    "host": {
        # Semantic chunk that only captured the dollar allowance, missing the prohibition chunk
        "title": "Handbook Section 4.3 — Lodging & Transportation",
        "snippet": "Staying with a friend or relative allows a host gift of up to US $50 per day with valid receipts. Expenses must be submitted via Concur.",
        "link": "https://hr-portal.altostrat.com/handbook#4.3-lodging-transportation"
    },
    "gift card": {
        "title": "Handbook Section 4.3 — Lodging & Transportation",
        "snippet": "Staying with a friend or relative allows a host gift of up to US $50 per day with valid receipts.",
        "link": "https://hr-portal.altostrat.com/handbook#4.3-lodging-transportation"
    },
    "salon": {
        # Semantic chunk that only captured the approval tiers table, missing the prohibited venue category chunk
        "title": "Handbook Section 5.2 — Commercial Gifts & Entertainment",
        "snippet": "Written Pre-Approval Thresholds (Non-Government): Under US $100 per person: No pre-approval required. US $100 to US $250: Written pre-approval from Manager. US $250 to US $500: Director approval.",
        "link": "https://hr-portal.altostrat.com/handbook#5.2-gifts-entertainment"
    },
    "room salon": {
        "title": "Handbook Section 5.2 — Commercial Gifts & Entertainment",
        "snippet": "Written Pre-Approval Thresholds (Non-Government): Under US $100 per person: No pre-approval required. US $100 to US $250: Written pre-approval from Manager.",
        "link": "https://hr-portal.altostrat.com/handbook#5.2-gifts-entertainment"
    },
}

def search_policy_docs(query: str) -> dict:
    """Semantic search over the HR policy corpus in Vertex AI Search."""
    q_low = query.lower()

    if discoveryengine and config.GOOGLE_CLOUD_PROJECT:
        project_id = config.GOOGLE_CLOUD_PROJECT
        location = config.VERTEX_AI_SEARCH_LOCATION or "global"
        engine_id = config.VERTEX_AI_SEARCH_ENGINE_ID or "hr-policies-lab-engine"

        client_options = (
            ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
            if location != "global"
            else None
        )
        try:
            client = discoveryengine.SearchServiceClient(client_options=client_options)
            serving_config = (
                f"projects/{project_id}/locations/{location}/collections/default_collection"
                f"/engines/{engine_id}/servingConfigs/default_search"
            )
            content_spec = discoveryengine.SearchRequest.ContentSearchSpec(
                extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                    max_extractive_answer_count=3,
                    max_extractive_segment_count=3,
                )
            )
            request = discoveryengine.SearchRequest(
                serving_config=serving_config,
                query=query,
                page_size=5,
                content_search_spec=content_spec,
            )
            response = client.search(request)
            snippets = []
            citations = []
            for result in response.results:
                doc = result.document
                data = getattr(doc, "derived_struct_data", {}) or {}
                title = data.get("title", "")
                link = data.get("link", "")
                if link and link not in citations:
                    citations.append(link)
                extracted_texts = []
                for seg in data.get("extractive_segments", []):
                    content = seg.get("content") if hasattr(seg, "get") else getattr(seg, "content", None)
                    if content:
                        extracted_texts.append(content)
                if extracted_texts:
                    snippets.append(f"[{title}] ({link}):\n" + "\n".join(extracted_texts))
            if snippets:
                return {"grounded_context": "\n\n".join(snippets), "citations": citations}
        except Exception:
            pass  # Fall back to canonical mock semantic retriever for local testing

    # Fallback to simulated RAG semantic chunk retrieval
    for k, v in MOCK_DATABASE.items():
        if k in q_low:
            return {
                "grounded_context": f"[{v['title']}] ({v['link']}):\n{v['snippet']}",
                "citations": [v["link"]]
            }

    return {"grounded_context": "", "citations": []}
