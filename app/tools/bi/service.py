# app/tools/bi/service.py

from typing import Dict, List, Tuple


def get_bi_reports() -> List[Dict]:
    """Central BI report registry (easy to move into DB later)."""
    return [
        {
            "title": "Business 360",
            "description": "Executive 360° view of business performance with high-level KPIs and drilldowns.",
            "category": "Executive",
            "tags": ["KPIs", "360"],
            "iframe_src": "https://app.powerbi.com/view?r=eyJrIjoiZDdlNzRmODQtNGFkNi00OTMxLThiMDItMTQxMzU3MjE1NDkzIiwidCI6IjdkODViMzVjLTg3MmUtNDA1NS1hZjkyLTgwZmI3YzlmOTRiNCIsImMiOjF9",
        },
        {
            "title": "Workflow Analysis",
            "description": "Daily workflow visibility and operational bottleneck analysis.",
            "category": "Operations",
            "tags": ["Workflow", "Daily"],
            "iframe_src": "https://app.powerbi.com/view?r=eyJrIjoiNGNmOTk1OGItYmQxMi00ZDMwLTgzNmYtODAxYTNkMjcxYmYxIiwidCI6IjdkODViMzVjLTg3MmUtNDA1NS1hZjkyLTgwZmI3YzlmOTRiNCIsImMiOjF9",
        },
        {
            "title": "Workflow Analysis (Allowed Amount)",
            "description": "Workflow + allowed amount to connect operational activity to financial impact.",
            "category": "Operations",
            "tags": ["Allowed $", "Workflow"],
            "iframe_src": "https://app.powerbi.com/view?r=eyJrIjoiZTdkNGIyNDgtNTBhOS00ZDcxLWI1ZmItYjdlMGFiOWRjZjE5IiwidCI6IjdkODViMzVjLTg3MmUtNDA1NS1hZjkyLTgwZmI3YzlmOTRiNCIsImMiOjF9",
        },
        {
            "title": "Call Analysis",
            "description": "Inbound call analytics to improve staffing, response time, and call outcomes.",
            "category": "Contact Center",
            "tags": ["Calls", "Inbound"],
            "iframe_src": "https://app.powerbi.com/view?r=eyJrIjoiNWQ1OWU4ZTAtM2UwZS00MThiLTk5ODQtMGJjN2FjMzk3Y2Y0IiwidCI6IjdkODViMzVjLTg3MmUtNDA1NS1hZjkyLTgwZmI3YzlmOTRiNCIsImMiOjF9",
        },
        {
            "title": "True Upcare",
            "description": "Opportunity dashboard to identify growth levers, gaps, and actionable next steps.",
            "category": "Growth",
            "tags": ["Opportunity", "Growth"],
            "iframe_src": "https://app.powerbi.com/view?r=eyJrIjoiMjllNmFiZjMtZGIwMy00YTgxLThiOTQtMGI4YTdhMTJjNzhiIiwidCI6IjdkODViMzVjLTg3MmUtNDA1NS1hZjkyLTgwZmI3YzlmOTRiNCIsImMiOjF9",
        },
        {
            "title": "Inventory Optimization",
            "description": "Reduce stockouts, improve turns, and right-size purchasing.",
            "category": "Supply Chain",
            "tags": ["Inventory", "Optimization"],
            "iframe_src": "https://app.powerbi.com/view?r=eyJrIjoiOTIzYzA3OWItNzAxMC00MGUwLWI3MWMtY2JjNDVmZWNlY2RmIiwidCI6IjdkODViMzVjLTg3MmUtNDA1NS1hZjkyLTgwZmI3YzlmOTRiNCIsImMiOjF9",
        },
        {
            "title": "Delivery Optimization",
            "description": "Routing efficiency + driver monitoring for performance management.",
            "category": "Logistics",
            "tags": ["Delivery", "Drivers"],
            "iframe_src": "https://app.powerbi.com/view?r=eyJrIjoiYzdhMDdiZDYtZDJlMi00YjkzLWI4NWQtMGUzZTY2ZjIzZTA0IiwidCI6IjdkODViMzVjLTg3MmUtNDA1NS1hZjkyLTgwZmI3YzlmOTRiNCIsImMiOjF9",
        },
        {
            "title": "Expire Prescription Retrieval",
            "description": "Identify expiring prescriptions and recovery opportunities.",
            "category": "Clinical Ops",
            "tags": ["Rx", "Retrieval"],
            "iframe_src": "https://app.powerbi.com/view?r=eyJrIjoiNmY2ZTkxYWYtYTJkNy00OGYxLWJkMzktYmRmZWQwMzNiZmIyIiwidCI6IjdkODViMzVjLTg3MmUtNDA1NS1hZjkyLTgwZmI3YzlmOTRiNCIsImMiOjF9",
        },
        {
            "title": "Templates Resupply",
            "description": "Template dashboard (demo) to standardize and accelerate reporting.",
            "category": "Templates",
            "tags": ["Template", "Resupply"],
            "iframe_src": "https://app.powerbi.com/view?r=eyJrIjoiZTY2ZWQ2NTUtMmNkMy00MjkxLWIzODQtMThhMzc0N2VjZjI3IiwidCI6IjY2ZTU0MjFhLTIwNzYtNDQyYS04MDc1LTFjMTQyMzliNDg3NyJ9",
        },
        {
            "title": "Maximum Gross Potential",
            "description": "Quantify upside and prioritize action areas for leadership.",
            "category": "Executive",
            "tags": ["MGP", "Opportunity"],
            "iframe_src": "https://app.powerbi.com/view?r=eyJrIjoiZmU3M2M5Y2QtZGQwMS00ODhjLWI0ZWYtM2FjODAzNmUxZWMzIiwidCI6IjY2ZTU0MjFhLTIwNzYtNDQyYS04MDc1LTFjMTQyMzliNDg3NyJ9",
        },
    ]


def get_categories(reports: List[Dict]) -> List[str]:
    cats = sorted({(r.get("category") or "Other") for r in reports})
    return cats
