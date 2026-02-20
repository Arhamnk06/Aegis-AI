import streamlit as st
import pandas as pd
import numpy as np
from src.data import load_sample_csv, generate_simulated_signals, validate_dataframe
from datetime import datetime
from src.logic import (
    enrich_dataframe,
    generate_ai_explanation,
    recommend_intervention,
    estimate_enterprise_impact,
    get_owner_team,
    get_sla,
)


def render_overview():
    """Render the Overview page with KPIs, trend chart, and context."""
    st.title("Aegis AI")
    st.subheader("Enterprise Risk & Harm Prevention Platform")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Risk Signals", "142", "+12")
    col2.metric("High Severity Alerts", "23", "+3")
    col3.metric("Avg Confidence", "0.81", "+0.02")
    col4.metric("System Status", "Operational")

    st.divider()
    st.subheader("Risk Signal Trend (Last 30 Days)")

    np.random.seed(7)
    days = 30
    trend_data = pd.DataFrame({
        "Mental Health": np.clip(np.cumsum(np.random.randn(days) * 0.5) + 20, 5, 40),
        "Service Load": np.clip(np.cumsum(np.random.randn(days) * 0.4) + 15, 3, 35),
        "Fraud": np.clip(np.cumsum(np.random.randn(days) * 0.6) + 10, 2, 30),
        "Misinformation": np.clip(np.cumsum(np.random.randn(days) * 0.3) + 8, 1, 25),
    })
    st.line_chart(trend_data)

    st.divider()
    st.subheader("Why This Matters")
    st.info(
        "Organizations face an increasing volume of risk signals across domains — from employee wellness "
        "to cybersecurity threats. Aegis AI provides a unified, AI-powered platform to detect, classify, "
        "and respond to these signals in real time. By combining responsible AI governance with enterprise-grade "
        "architecture, Aegis AI helps decision-makers act quickly, transparently, and ethically — reducing harm "
        "while maintaining full auditability."
    )


def render_risk_analysis():
    """Render the Risk Analysis page with upload, simulation, and decision cards."""
    st.title("Risk Analysis")
    st.markdown("Upload your own risk signals or use simulated data to explore the analysis pipeline.")
    st.divider()

    df = None

    col_a, col_b = st.columns(2)
    with col_a:
        uploaded = st.file_uploader("Option A: Upload CSV", type=["csv"])
        if uploaded is not None:
            try:
                df = pd.read_csv(uploaded)
                valid, msg = validate_dataframe(df)
                if not valid:
                    st.error(f"Validation failed: {msg}")
                    df = None
                else:
                    st.success("File uploaded and validated successfully.")
            except Exception as e:
                st.error(f"Could not read file. Please upload a valid CSV. Error: {e}")
                df = None

    with col_b:
        st.markdown("**Option B: Use Simulated Data**")
        if st.button("Load Simulated Dataset", key="sim_btn"):
            st.session_state["risk_df"] = generate_simulated_signals(30, "general")

    if df is not None:
        st.session_state["risk_df"] = df

    if "risk_df" in st.session_state and st.session_state["risk_df"] is not None:
        df = st.session_state["risk_df"]
        st.subheader("Data Preview")
        st.dataframe(df.head(10), use_container_width=True)

        enriched = enrich_dataframe(df)
        enriched = enriched.sort_values("severity_score", ascending=False).reset_index(drop=True)
        st.divider()

        critical_alerts = enriched[enriched["risk_level"] == "Critical"]
        if len(critical_alerts) > 0:
            st.subheader(f"Critical Alerts ({len(critical_alerts)})")
            crit_cols = ["timestamp", "category", "severity_score", "confidence_score", "description"]
            crit_available = [c for c in crit_cols if c in critical_alerts.columns]
            st.dataframe(critical_alerts[crit_available], use_container_width=True)
            st.divider()

        st.subheader("Enriched Risk Analysis")
        display_cols = ["timestamp", "category", "severity_score", "risk_level", "anomaly_flag", "confidence_score", "description"]
        available_cols = [c for c in display_cols if c in enriched.columns]
        st.dataframe(enriched[available_cols], use_container_width=True)

        st.divider()
        st.subheader("Decision Card Generator")
        max_idx = len(enriched) - 1
        selected_idx = st.number_input(
            "Select row index to inspect",
            min_value=0,
            max_value=max_idx,
            value=0,
            step=1,
        )

        if st.button("Generate Decision Card", key="decision_card_btn"):
            row = enriched.iloc[selected_idx]
            _render_decision_card(row)


def _render_decision_card(row):
    """Render a Decision Card for a single risk signal row."""
    risk_level = row["risk_level"]
    severity = row["severity_score"]
    category = row["category"]
    anomaly = row["anomaly_flag"]
    description = row["description"]
    confidence = row["confidence_score"]
    impact = estimate_enterprise_impact(risk_level)

    explanation = generate_ai_explanation(category, severity, anomaly, description)
    intervention = recommend_intervention(category, risk_level, anomaly)

    level_colors = {
        "Critical": "error",
        "High": "warning",
        "Medium": "info",
        "Low": "success",
    }
    alert_type = level_colors.get(risk_level, "info")

    with st.container():
        st.markdown("---")
        st.markdown(f"### Decision Card — Row {row.name}")

        getattr(st, alert_type)(f"**Risk Level: {risk_level}**")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Category:** {category.replace('_', ' ').title()}")
            st.markdown(f"**Severity Score:** {severity:.2f}")
        with col2:
            st.markdown(f"**Anomaly Detected:** {'Yes' if anomaly else 'No'}")
            st.markdown(f"**Estimated Enterprise Impact:** {impact}")

        st.markdown(explanation)

        st.success(f"**Recommended Intervention:** {intervention}")

        st.metric("Confidence Score", f"{confidence:.2f}")

        st.caption(f"Audit Log: Event recorded at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        with st.expander("Model Transparency"):
            st.markdown(
                "- **Inputs evaluated:** category, severity_score, description\n"
                "- **Risk tiering:** Deterministic thresholds (Low < 0.35, Medium < 0.6, High < 0.8, Critical >= 0.8)\n"
                "- **Anomaly detection:** Category-specific thresholds and score >= 0.9\n"
                "- **Confidence:** Heuristic calibration based on severity and anomaly\n"
                "- **Human-in-the-loop:** Required for final decision"
            )


def render_responsible_ai():
    """Render the Responsible AI & Governance page."""
    st.title("Responsible AI & Governance")
    st.markdown("Aegis AI is built on principles of transparency, fairness, and accountability.")
    st.divider()

    st.subheader("Privacy by Design")
    st.markdown(
        "- No personal data is stored by default; all signals are processed statelessly\n"
        "- Sensitive information (emails, phone numbers) is automatically redacted before display\n"
        "- Data retention policies are configurable per deployment and default to zero-retention\n"
        "- All data processing follows the principle of minimal necessary access"
    )

    st.subheader("Human-in-the-Loop Policy")
    st.markdown(
        "- AI generates recommendations — **humans make all final decisions**\n"
        "- Every AI output includes a mandatory advisory disclaimer\n"
        "- Critical-severity decisions require explicit human approval before action\n"
        "- Escalation paths ensure no automated action is taken without oversight"
    )

    st.subheader("Bias & Fairness Considerations")
    st.markdown(
        "- Risk models are regularly audited for demographic and category-level bias\n"
        "- Protected group attributes are never used as direct model inputs\n"
        "- Drift detection monitors are deployed to flag shifts in model behavior\n"
        "- Fairness metrics (equalized odds, demographic parity) are tracked per release cycle"
    )

    st.subheader("Audit Logging Plan")
    st.markdown(
        "- Every risk classification decision is logged with timestamp, inputs, and outputs\n"
        "- Human override actions are recorded with rationale for compliance review\n"
        "- Model version and configuration are captured per inference call\n"
        "- Logs are immutable and stored in tamper-evident audit storage"
    )

    st.subheader("Failure Modes & Mitigations")
    st.warning(
        "**Known failure modes and how Aegis AI addresses them:**"
    )
    st.markdown(
        "- **False positives:** Confidence scores and human review gates reduce unnecessary escalation\n"
        "- **Hallucinations:** Rule-based logic (not generative AI) eliminates confabulation risk in core analysis\n"
        "- **Over-reliance:** Mandatory advisory disclaimers and training materials reinforce critical thinking\n"
        "- **Data quality issues:** Input validation catches missing or malformed data before analysis\n"
        "- **Model degradation:** Scheduled revalidation cycles and drift detection ensure ongoing accuracy"
    )


def render_enterprise_architecture():
    """Render the Enterprise Architecture page."""
    st.title("Enterprise Architecture")
    st.markdown("Aegis AI is designed for production-grade deployment in regulated industries.")
    st.divider()

    st.subheader("System Architecture")
    st.code(
        """
┌─────────────────────────────────────────────────────────────┐
│                      LOAD BALANCER                          │
│                    (TLS Termination)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  API Gateway │ │  API Gateway │ │  API Gateway │
│  (Stateless) │ │  (Stateless) │ │  (Stateless) │
│  Rate Limit  │ │  Rate Limit  │ │  Rate Limit  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        ▼
         ┌──────────────────────────┐
         │    INFERENCE SERVICE     │
         │  (Horizontally Scaled)   │
         │  Risk Classification     │
         │  Anomaly Detection       │
         │  Confidence Scoring      │
         └────────────┬─────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  Encrypted   │ │  Audit   │ │  Monitoring  │
│  Data Store  │ │   Log    │ │  & Alerting  │
│  (AES-256)   │ │ (Immut.) │ │  (Prometheus)│
└──────────────┘ └──────────┘ └──────────────┘
        """,
        language=None,
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Stateless API Layer")
        st.markdown("Each API gateway instance is stateless, enabling horizontal scaling and zero-downtime deployments.")

        st.markdown("#### Scalable Inference Service")
        st.markdown("Risk classification, anomaly detection, and confidence scoring run on auto-scaled compute nodes with request queuing.")

        st.markdown("#### Encrypted Storage")
        st.markdown("All data at rest is encrypted with AES-256. In-transit encryption uses TLS 1.3. Key management follows FIPS 140-2 standards.")

    with col2:
        st.markdown("#### Role-Based Access Control")
        st.markdown("RBAC with least-privilege defaults. Roles: Viewer, Analyst, Admin, Compliance Officer. All access is logged.")

        st.markdown("#### Monitoring & Alerting")
        st.markdown("Real-time dashboards via Prometheus and Grafana. Automated alerts for latency spikes, error rates, and capacity thresholds.")

        st.markdown("#### Rate Limiting")
        st.markdown("Per-client rate limiting at the API gateway layer prevents abuse and ensures fair resource allocation across tenants.")

    st.divider()
    st.subheader("Why IBM Z")
    st.info(
        "IBM Z mainframes provide unmatched reliability for mission-critical workloads. Key advantages for Aegis AI:\n\n"
        "- **99.999% uptime** — essential for healthcare and financial risk monitoring that cannot tolerate downtime\n"
        "- **Hardware-accelerated encryption** — on-chip cryptographic processing enables real-time encryption at scale without performance penalty\n"
        "- **High-volume transaction processing** — capable of processing billions of transactions per day, ideal for financial fraud detection\n"
        "- **Secure enclave computing** — IBM Secure Execution ensures data confidentiality even from system administrators\n"
        "- **Regulatory compliance** — built-in compliance features for HIPAA, PCI-DSS, GDPR, and SOX requirements\n"
        "- **Vertical scalability** — single-system scaling reduces distributed systems complexity for latency-sensitive workloads"
    )

    st.divider()
    st.subheader("Business Model")
    st.markdown("Aegis AI follows a tiered SaaS model designed for enterprise adoption:")

    tiers = pd.DataFrame({
        "Tier": ["Starter", "Professional", "Enterprise"],
        "Signals/Month": ["10,000", "100,000", "Unlimited"],
        "Users": ["5", "25", "Unlimited"],
        "SLA": ["99.5%", "99.9%", "99.99%"],
        "Support": ["Email", "Priority", "Dedicated CSM"],
        "Features": [
            "Core risk analysis, basic reporting",
            "Full analysis suite, API access, custom rules",
            "Custom models, on-prem option, audit compliance pack",
        ],
    })
    st.table(tiers)


def render_demo_mode():
    """Render the Demo Mode page with scenario buttons and pitch scripts."""
    st.title("Demo Mode")
    st.markdown("Select a scenario to load a pre-configured dataset and see Aegis AI in action.")
    st.divider()

    scenarios = {
        "university_exam_stress": {
            "label": "Load University Exam Stress Scenario",
            "sdg": "**SDG Alignment:** SDG 3 (Good Health & Well-being), SDG 4 (Quality Education) — "
                   "Aegis AI helps institutions detect early signs of student mental health crises during "
                   "high-pressure academic periods, enabling timely intervention and support.",
            "pitch": (
                "Imagine it's finals week at a major university. Counseling centers are overwhelmed, "
                "online exam platforms are buckling, and rumors about schedule changes are spreading. "
                "Aegis AI monitors these signals in real time — flagging critical stress indicators, "
                "predicting service bottlenecks, and filtering misinformation. With Aegis AI, administrators "
                "can act before a crisis escalates, not after. Every recommendation comes with full transparency "
                "and a human-in-the-loop safeguard."
            ),
        },
        "healthcare_capacity": {
            "label": "Load Healthcare Capacity Scenario",
            "sdg": "**SDG Alignment:** SDG 3 (Good Health & Well-being) — "
                   "Aegis AI supports healthcare systems in managing capacity surges, protecting "
                   "frontline worker wellness, and maintaining care quality under pressure.",
            "pitch": (
                "A regional hospital network is facing a surge in emergency admissions. ICU beds are running low, "
                "staff burnout is spiking, and fraudulent billing claims are mixed into the chaos. "
                "Aegis AI provides a unified risk dashboard — surfacing the most critical capacity signals, "
                "flagging anomalies in real time, and recommending concrete interventions. The system never acts "
                "alone: every alert includes a confidence score and requires human approval. This is AI that "
                "supports healthcare professionals, not replaces them."
            ),
        },
        "financial_fraud": {
            "label": "Load Financial Fraud Scenario",
            "sdg": "**SDG Alignment:** SDG 16 (Peace, Justice & Strong Institutions) — "
                   "Aegis AI strengthens financial integrity by detecting fraud patterns, protecting "
                   "consumers, and supporting regulatory compliance.",
            "pitch": (
                "A financial institution is seeing unusual patterns: synthetic identities in new accounts, "
                "micro-transaction probing, and phishing campaigns targeting customers. Traditional rule-based "
                "systems are overwhelmed by the volume. Aegis AI uses multi-signal analysis to detect, classify, "
                "and prioritize fraud risks — from critical account freezes to routine monitoring. Every decision "
                "is auditable, every recommendation transparent. This is responsible AI for the enterprise."
            ),
        },
    }

    for scenario_key, config in scenarios.items():
        if st.button(config["label"], key=f"demo_{scenario_key}"):
            st.session_state["demo_scenario"] = scenario_key

    if "demo_scenario" in st.session_state:
        scenario_key = st.session_state["demo_scenario"]
        config = scenarios[scenario_key]

        df = generate_simulated_signals(30, scenario_key)
        enriched = enrich_dataframe(df)
        enriched = enriched.sort_values("severity_score", ascending=False).reset_index(drop=True)

        scenario_name = config["label"].replace("Load ", "").replace(" Scenario", "")

        top_alerts = enriched.nlargest(3, "severity_score")
        top_categories = enriched["category"].value_counts().head(2)

        st.divider()
        st.subheader("Scenario Summary")
        st.markdown(f"**Scenario Loaded:** {scenario_name}")

        top_cat_str = ", ".join([f"{cat.replace('_', ' ').title()} ({cnt})" for cat, cnt in top_categories.items()])
        critical_count = len(enriched[enriched["risk_level"] == "Critical"])
        high_count = len(enriched[enriched["risk_level"] == "High"])
        anomaly_count = len(enriched[enriched["anomaly_flag"]])

        st.info(
            f"**Executive Summary:** This scenario contains {len(enriched)} risk signals with "
            f"{critical_count} critical and {high_count} high-severity alerts. "
            f"{anomaly_count} anomalies were detected requiring immediate attention. "
            f"Recommended response: prioritize critical alerts, assign owner teams, and initiate escalation protocols."
        )
        st.markdown(f"**Primary Categories:** {top_cat_str}")

        st.divider()
        st.subheader("Top Critical Alerts (Immediate Action Required)")

        for _, row in top_alerts.iterrows():
            risk_level = row["risk_level"]
            impact = estimate_enterprise_impact(risk_level)
            owner = get_owner_team(row["category"])
            sla = get_sla(risk_level)

            with st.container():
                st.error(
                    f"**{row['category'].replace('_', ' ').title()}** — "
                    f"Severity: {row['severity_score']:.2f} | "
                    f"Risk: {risk_level} | "
                    f"Confidence: {row['confidence_score']:.2f}\n\n"
                    f"Anomaly Detected: {'Yes' if row['anomaly_flag'] else 'No'} | "
                    f"Estimated Impact: {impact} | "
                    f"Recommended Owner: {owner} | "
                    f"SLA: {sla}\n\n"
                    f"{row['description']}"
                )

        st.divider()
        st.subheader("Recommended Actions Queue")
        actions_data = []
        for _, row in top_alerts.iterrows():
            risk_level = row["risk_level"]
            owner = get_owner_team(row["category"])
            sla = get_sla(risk_level)
            intervention = recommend_intervention(row["category"], risk_level, row["anomaly_flag"])
            actions_data.append({
                "Action": intervention[:120] + "..." if len(intervention) > 120 else intervention,
                "Owner": owner,
                "SLA": sla,
                "Status": "Pending",
            })
        st.table(pd.DataFrame(actions_data))

        st.divider()
        anomalies = enriched[enriched["anomaly_flag"]]
        st.subheader(f"Anomalies Detected: {len(anomalies)}")
        if len(anomalies) > 0:
            st.dataframe(
                anomalies[["timestamp", "category", "severity_score", "risk_level", "confidence_score", "description"]],
                use_container_width=True,
            )
        else:
            st.success("No anomalies detected in this scenario.")

        st.divider()
        st.subheader("SDG Alignment")
        st.info(config["sdg"])

        st.divider()
        st.subheader("Live Demo Script")
        st.text_area(
            "Read this during the live demo:",
            value=config["pitch"],
            height=200,
            key=f"pitch_{scenario_key}",
        )

        st.divider()
        st.markdown("#### Full Enriched Dataset")
        st.dataframe(enriched, use_container_width=True)


def render_footer():
    """Render the app footer."""
    st.divider()
    st.caption("Aegis AI demo. Not for clinical or legal decisions.")
