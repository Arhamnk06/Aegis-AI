# Aegis AI — Enterprise Risk & Harm Prevention Platform

## Overview

Aegis AI is a Streamlit-based web application that serves as an enterprise-grade risk and harm prevention platform. It provides risk signal analysis, responsible AI governance dashboards, and enterprise architecture visualization. The app is designed as a polished hackathon demo that demonstrates responsible AI governance, SDG alignment, and enterprise thinking around scalability, reliability, and security.

The application runs via `streamlit run app.py --server.port 5000` and features a multi-page layout with sidebar navigation across five sections: Overview, Risk Analysis, Responsible AI & Governance, Enterprise Architecture, and Demo Mode.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Application Structure

The project follows a clean separation of concerns with a flat Python package structure:

- **`app.py`** — Entry point. Configures the Streamlit page, sets up sidebar navigation, and routes to the appropriate page renderer.
- **`src/ui.py`** — All UI rendering functions (`render_overview`, `render_risk_analysis`, `render_responsible_ai`, `render_enterprise_architecture`, `render_demo_mode`, `render_footer`). Each page is a standalone function.
- **`src/logic.py`** — Core business logic: risk level classification, anomaly detection, confidence score computation, PII redaction, and AI explanation generation. Pure functions with no UI dependencies.
- **`src/data.py`** — Data layer: loads sample CSV from `assets/sample_signals.csv` and generates simulated risk signal DataFrames with configurable scenarios.
- **`assets/sample_signals.csv`** — Built-in sample dataset with 30 rows, columns: `timestamp`, `category`, `severity_score`, `description`.

### Key Design Decisions

**Frontend Framework: Streamlit**
- Chosen for rapid prototyping and polished demo appearance.
- Uses built-in widgets (`st.metric`, `st.line_chart`, `st.radio`, `st.dataframe`, `st.columns`, `st.container`).

**Data Processing: Pandas + NumPy**
- Risk signals are represented as Pandas DataFrames throughout the pipeline.
- No database — data is either uploaded via CSV, loaded from a static file, or generated in-memory.

**Risk Classification Pipeline**
- Severity scores (0.0–1.0) classified into: Low (<0.35), Medium (<0.6), High (<0.8), Critical (>=0.8).
- Anomaly detection uses category-specific thresholds plus global >=0.9 flag.
- Confidence scores bounded between 0.55 and 0.95.

**Multi-Page Navigation**
- Implemented via `st.radio` in the sidebar.
- Pages: Overview, Risk Analysis, Responsible AI & Governance, Enterprise Architecture, Demo Mode.

### Data Schema

Required columns:
| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | datetime | When the signal was detected |
| `category` | string | mental_health, service_load, fraud, misinformation |
| `severity_score` | float | 0.0 to 1.0 |
| `description` | string | Human-readable description |

Computed columns:
| Column | Type | Description |
|--------|------|-------------|
| `risk_level` | string | Low / Medium / High / Critical |
| `anomaly_flag` | boolean | Whether the signal is anomalous |
| `confidence_score` | float | 0.55 to 0.95 |

## External Dependencies

### Python Packages
- **Streamlit** — Web application framework
- **Pandas** — DataFrame operations
- **NumPy** — Numerical computations

### No External Services
- No database connections
- No external APIs
- No authentication system
