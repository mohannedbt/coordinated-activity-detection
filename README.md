# 🛡️ BehaviorGuard — Behavioral Risk Intelligence Platform

BehaviorGuard is an end-to-end **behavioral risk detection and moderation intelligence platform** designed to identify spam, coordinated campaigns, and abnormal user behavior using **explainable risk scoring**. The system bridges the gap between raw data and human decision-making by combining a **Python ML backend (FastAPI)** with a polished **ASP.NET Core 8 MVC dashboard**.

---

## 🏗️ Architecture Overview

The platform is split into two independent services that communicate via a RESTful API:

1.  **FastAPI Backend (Python)**: The analytical "brain" that executes the ML pipeline, calculates risk scores, and performs behavioral clustering.
2.  **ASP.NET Core MVC Dashboard (.NET 8)**: The "face" of the platform, providing moderators with interactive visualizations, ranked tables, and session management.



---

## ⚙️ The MVP Pipeline (Python Logic)

The core logic resides in the `run_mvp_pipeline` function. It transforms raw CSV data into actionable intelligence through a structured flow:

* **Data Ingestion**: Reads a CSV containing `post_id`, `text`, `timestamp`, `account_id`, and `account_age_days`.
* **Risk Engine Execution**: Uses the `RiskPipeline` to generate base `risk_score` and `confidence` metrics for every post.
* **Policy Enforcement**: Applies a `decision_policy` that automatically classifies posts into `AUTO_ACTION`, `QUEUE_REVIEW`, or `NO_ACTION` based on risk thresholds.
* **Trend Tracking (EWMA)**: Computes an **Exponentially Weighted Moving Average (EWMA)** for account risk. This identifies if a user's behavior is escalating over time rather than judging them on a single isolated post.
* **Multi-Dimensional Aggregation**: 
    * **Account View**: Aggregates total posts, average risk, and risk trends for every user.
    * **Cluster View**: Groups posts by `behavior_cluster` (derived via HDBSCAN) to detect coordinated bot-net activity.
* **Serialization**: Packages the data into a JSON-ready format for the .NET UI.

---

## 🖥️ The .NET 8 Dashboard (UI/UX)

The frontend is designed for **Explainable AI (XAI)**, ensuring moderators understand *why* a decision was made rather than just seeing a flag.

### 1. Analytics Dashboard (`Index.cshtml`)
* **KPI Cards**: High-level counters for **Total Posts**, **Auto Actions**, and **Average Risk Score**.
* **Interactive Charts (Chart.js)**: 
    * **Decision Breakdown**: A doughnut chart displaying the ratio of moderation actions.
    * **Risk Distribution**: A bar chart segmenting posts into High, Med, and Low risk buckets.
* **Ranked Post Analysis**: A table that automatically ranks posts by the highest risk score. It features **AJAX-driven pagination** to handle large datasets smoothly without page refreshes.



### 2. Account Risk Profiles
* **Risk Profiles**: Lists accounts by their aggregate threat level.
* **Trend Visualization**: Displays the EWMA trend to show if an account is becoming more dangerous.
* **Direct Intervention**: Integrated buttons allow moderators to "Restrict" accounts immediately based on the pipeline's max_risk score.

---

## 🛠️ Setup and Installation

### 1. Backend Setup (FastAPI)
```bash
# Navigate to the api directory
cd api
pip install -r requirements.txt
```
```bash
# Start the FastAPI server

uvicorn main:app --reload --port 8000
```
### 2. Frontend Setup (ASP.NET Core)
**Open the Project**: Open the solution in your preferred editor (e.g., Visual Studio 2022 or VS Code).

**Configure API Endpoint:** Ensure the DashboardController or the frontend fetch logic is configured to communicate with the FastAPI backend at http://localhost:8000.

**Run the Project:** Launch the application (press F5 or use dotnet run).

**📁 Project Structure**

```
api/               # FastAPI endpoints and session handling
engine/            # The ML Engine (Pipeline, Detectors, XAI)
UI/                # ASP.NET Core MVC (Controllers, Views, wwwroot)
data/              # Data storage and temporary session uploads
```
**🧠 Design Philosophy**
***"Moderation systems should explain before they enforce."***

BehaviorGuard prioritizes Human-in-the-loop moderation. By providing transparency through confidence scores and categorical risk drivers, the platform empowers moderators to act with precision and speed.