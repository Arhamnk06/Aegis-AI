import re
import numpy as np


def calculate_risk_level(score: float) -> str:
    """Classify a severity score into a risk level."""
    if score < 0.35:
        return "Low"
    elif score < 0.6:
        return "Medium"
    elif score < 0.8:
        return "High"
    else:
        return "Critical"


CATEGORY_ANOMALY_THRESHOLDS = {
    "mental_health": 0.80,
    "service_load": 0.85,
    "fraud": 0.75,
    "misinformation": 0.78,
}


def detect_anomaly(score: float, category: str) -> bool:
    """Detect whether a signal is anomalous based on category-specific thresholds."""
    if score >= 0.9:
        return True
    threshold = CATEGORY_ANOMALY_THRESHOLDS.get(category, 0.80)
    return score >= threshold


def compute_confidence(score: float, anomaly: bool) -> float:
    """Compute a confidence score between 0.55 and 0.95."""
    base = 0.55 + (score * 0.35)
    if anomaly:
        base += 0.05
    return round(min(max(base, 0.55), 0.95), 2)


def redact_sensitive(text: str) -> str:
    """Remove emails and phone-like patterns from text."""
    text = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[REDACTED_EMAIL]", text)
    text = re.sub(r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}", "[REDACTED_PHONE]", text)
    return text


ENTERPRISE_IMPACT = {
    "Low": "Minor",
    "Medium": "Moderate",
    "High": "Significant",
    "Critical": "Severe",
}


def estimate_enterprise_impact(risk_level: str) -> str:
    """Map risk level to enterprise impact estimate."""
    return ENTERPRISE_IMPACT.get(risk_level, "Unknown")


OWNER_TEAM = {
    "mental_health": "Student Services",
    "service_load": "IT Ops",
    "fraud": "Security",
    "misinformation": "Comms",
}


def get_owner_team(category: str) -> str:
    """Map category to recommended owner team."""
    return OWNER_TEAM.get(category, "Operations")


def get_sla(risk_level: str) -> str:
    """Return SLA based on risk level."""
    if risk_level == "Critical":
        return "1 hour"
    elif risk_level == "High":
        return "24 hours"
    elif risk_level == "Medium":
        return "72 hours"
    return "1 week"


def generate_ai_explanation(category: str, severity_score: float, anomaly: bool, description: str) -> str:
    """Generate a professional AI explanation for a risk signal."""
    risk_level = calculate_risk_level(severity_score)

    category_context = {
        "mental_health": "psychological wellness and support service demand",
        "service_load": "infrastructure capacity and service availability",
        "fraud": "financial integrity and transaction security",
        "misinformation": "information accuracy and content authenticity",
    }

    risk_statements = {
        "Low": "Within normal operating parameters. Routine monitoring applies.",
        "Medium": "Elevated risk requiring monitoring.",
        "High": "Escalation threshold exceeded. Material operational risk.",
        "Critical": "Immediate action required. Potential systemic impact.",
    }

    context = category_context.get(category, "operational risk monitoring")
    statement = risk_statements.get(risk_level, "Assessment pending.")
    anomaly_text = " Anomaly detected: behavior deviates significantly from baseline." if anomaly else ""

    explanation = (
        f"**Analysis:** This signal relates to {context}. "
        f"{statement} "
        f"Severity score: {severity_score:.2f}. "
        f"Signal context: \"{redact_sensitive(description)}\".{anomaly_text}\n\n"
        f"*Recommendation is advisory and requires human review.*"
    )
    return explanation


def recommend_intervention(category: str, risk_level: str, anomaly: bool) -> str:
    """Return concrete enterprise intervention recommendations."""
    interventions = {
        ("mental_health", "Critical"): "Activate crisis response protocol. Deploy additional counseling resources. Notify wellness leadership team. Initiate 24-hour monitoring cycle.",
        ("mental_health", "High"): "Increase counseling availability. Send proactive outreach to at-risk groups. Schedule wellness check-ins within 48 hours.",
        ("mental_health", "Medium"): "Monitor wellness indicators. Prepare resource scaling plan. Review support service capacity.",
        ("mental_health", "Low"): "Continue routine monitoring. Log for trend analysis.",
        ("service_load", "Critical"): "Initiate capacity expansion protocol. Activate disaster recovery standby. Alert infrastructure on-call team. Consider load shedding non-critical services.",
        ("service_load", "High"): "Scale horizontal resources. Enable request queuing. Prepare failover activation.",
        ("service_load", "Medium"): "Monitor resource utilization trends. Pre-stage additional capacity. Review auto-scaling thresholds.",
        ("service_load", "Low"): "Log metrics for capacity planning. No immediate action required.",
        ("fraud", "Critical"): "Freeze affected accounts immediately. Escalate to fraud investigation unit. Preserve forensic evidence chain. Notify compliance officer.",
        ("fraud", "High"): "Flag transactions for manual review. Increase authentication requirements. Alert risk management team.",
        ("fraud", "Medium"): "Apply enhanced monitoring rules. Queue for next-cycle investigation. Update detection thresholds.",
        ("fraud", "Low"): "Log for pattern analysis. No immediate intervention required.",
        ("misinformation", "Critical"): "Issue immediate correction through official channels. Escalate to communications team. Implement content takedown if on owned platforms.",
        ("misinformation", "High"): "Prepare counter-narrative. Flag content for review. Alert communications stakeholders.",
        ("misinformation", "Medium"): "Monitor spread velocity. Prepare fact-check response. Log for trend analysis.",
        ("misinformation", "Low"): "Archive for reference. Continue baseline monitoring.",
    }

    base = interventions.get((category, risk_level), "Apply standard operating procedures for this risk category and level.")
    if anomaly:
        base += " **[ANOMALY DETECTED]** Escalate to senior analyst for pattern review and root cause investigation."
    return base


def enrich_dataframe(df):
    """Add risk_level, anomaly_flag, and confidence_score columns to a signals DataFrame."""
    df = df.copy()
    df["risk_level"] = df["severity_score"].apply(calculate_risk_level)
    df["anomaly_flag"] = df.apply(lambda r: detect_anomaly(r["severity_score"], r["category"]), axis=1)
    df["confidence_score"] = df.apply(lambda r: compute_confidence(r["severity_score"], r["anomaly_flag"]), axis=1)
    return df
