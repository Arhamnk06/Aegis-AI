import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def load_sample_csv() -> pd.DataFrame:
    """Load the built-in sample signals CSV from the assets folder."""
    df = pd.read_csv("assets/sample_signals.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def generate_simulated_signals(n: int = 30, scenario: str = "general") -> pd.DataFrame:
    """Generate a simulated risk signals DataFrame for a given scenario."""
    np.random.seed(42)
    base_time = datetime(2026, 2, 1, 6, 0, 0)

    scenario_configs = {
        "general": {
            "categories": ["mental_health", "service_load", "fraud", "misinformation"],
            "weights": [0.25, 0.25, 0.25, 0.25],
            "severity_range": (0.15, 0.95),
            "descriptions": {
                "mental_health": [
                    "Elevated stress indicators in student population",
                    "Increased counseling service demand detected",
                    "Wellness survey results show rising anxiety levels",
                    "After-hours crisis line volume above threshold",
                ],
                "service_load": [
                    "Server response time exceeding SLA targets",
                    "Queue depth growing on processing pipeline",
                    "Authentication service under heavy load",
                    "Database connection pool nearing capacity",
                ],
                "fraud": [
                    "Anomalous transaction pattern detected",
                    "Duplicate identity markers in new registrations",
                    "Unusual access pattern from unrecognized network",
                    "Rapid sequential approvals flagged by rules engine",
                ],
                "misinformation": [
                    "Coordinated inauthentic posting activity detected",
                    "Misleading health advisory circulating internally",
                    "Fabricated policy document shared on forum",
                    "Deepfake content detected in submitted materials",
                ],
            },
        },
        "university_exam_stress": {
            "categories": ["mental_health", "service_load", "misinformation"],
            "weights": [0.55, 0.30, 0.15],
            "severity_range": (0.30, 0.97),
            "descriptions": {
                "mental_health": [
                    "Spike in exam anxiety reported across multiple faculties",
                    "Crisis counseling requests exceed available capacity",
                    "Peer support network reporting burnout among volunteers",
                    "Sleep deprivation indicators elevated in residence surveys",
                    "Academic performance anxiety flagged in wellness screening",
                ],
                "service_load": [
                    "Online exam platform nearing concurrent user limit",
                    "Library reservation system overloaded during finals",
                    "Student portal response times degraded under load",
                ],
                "misinformation": [
                    "False exam schedule circulating on student groups",
                    "Misleading academic policy change rumor spreading online",
                ],
            },
        },
        "healthcare_capacity": {
            "categories": ["service_load", "mental_health", "fraud"],
            "weights": [0.50, 0.30, 0.20],
            "severity_range": (0.35, 0.98),
            "descriptions": {
                "service_load": [
                    "Emergency department intake at critical capacity",
                    "ICU bed availability below safety threshold",
                    "Patient scheduling backlog exceeding 72 hours",
                    "Lab processing queue depth at historic high",
                    "Ambulance diversion protocol triggered by overcrowding",
                ],
                "mental_health": [
                    "Healthcare worker burnout indicators at critical level",
                    "Staff absenteeism correlated with workload surge",
                    "Compassion fatigue screening flags rising among nurses",
                ],
                "fraud": [
                    "Suspicious billing pattern detected in claims processing",
                    "Duplicate patient records created under different identifiers",
                ],
            },
        },
        "financial_fraud": {
            "categories": ["fraud", "service_load", "misinformation"],
            "weights": [0.55, 0.25, 0.20],
            "severity_range": (0.40, 0.99),
            "descriptions": {
                "fraud": [
                    "Synthetic identity cluster detected in new account applications",
                    "Rapid micro-transaction pattern consistent with card testing",
                    "Cross-border wire transfers to flagged jurisdictions",
                    "Account takeover attempt using credential stuffing",
                    "Insider trading pattern detected in equity transactions",
                ],
                "service_load": [
                    "Transaction processing engine under abnormal load",
                    "Fraud detection pipeline latency exceeding SLA",
                    "Real-time scoring service nearing throughput limit",
                ],
                "misinformation": [
                    "Phishing campaign targeting customers with fake notices",
                    "Fabricated regulatory announcement causing market concern",
                ],
            },
        },
    }

    config = scenario_configs.get(scenario, scenario_configs["general"])
    categories = config["categories"]
    weights = config["weights"]
    sev_min, sev_max = config["severity_range"]
    descriptions = config["descriptions"]

    rows = []
    for i in range(n):
        cat = np.random.choice(categories, p=weights)
        severity = round(np.random.uniform(sev_min, sev_max), 2)
        ts = base_time + timedelta(hours=np.random.randint(0, 168))
        desc_options = descriptions.get(cat, ["Signal detected"])
        desc = np.random.choice(desc_options)
        rows.append({
            "timestamp": ts,
            "category": cat,
            "severity_score": severity,
            "description": desc,
        })

    df = pd.DataFrame(rows)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def validate_dataframe(df: pd.DataFrame) -> tuple[bool, str]:
    """Validate that a DataFrame has the required columns for risk analysis."""
    required = {"timestamp", "category", "severity_score", "description"}
    missing = required - set(df.columns)
    if missing:
        return False, f"Missing required columns: {', '.join(sorted(missing))}"
    return True, "All required columns present."
