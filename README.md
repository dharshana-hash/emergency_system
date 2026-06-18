# 🚨 Smart SOS Emergency System

A responsive, secure, data-driven Flask web application designed for real-time crisis triage management, role-based responder deployment, and live situational data visualization.

---

## 🛠️ System Architecture & Workflow

The application operates as an integrated triage engine that coordinates data flow securely across three core access levels:

1. **Civilian Intake Portal:** Public access routing where users can broadcast immediate SOS signals with coordinates and severity rankings.
2. **Field Responder Panel:** Authenticated view for volunteers to claim active cases and update dispatch lifecycle metrics.
3. **Crisis Command Center:** High-level administrative board hosting real-time status grids sorted dynamically by custom priority calculations, alongside live telemetry data dashboards.

---

## 🎛️ Core Features

* **Dynamic Triage Engine:** Calculates incident priority via an algorithmic formula combining pre-set disaster weights and user-defined severity indexes.
* **Role-Based Access Control (RBAC):** Passkey encryption protecting dedicated administrative and field unit routes.
* **Live Telemetry Visualization:** Embedded `Chart.js` data pipeline tracking threat ratios and incident resolution lifecycles dynamically.
* **Isolated Data Persistence:** Bypasses local folder permission conflicts using structured, self-contained instance storage paths.

---

## 🚀 Local Installation & Execution Guide

Follow these steps to run this platform locally on your machine:

### 1. Pre-requisites & Dependency Configuration
Ensure you have Python installed. Install the necessary ecosystem libraries:
```bash
pip install flask flask-sqlalchemy