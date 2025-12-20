# 🛡️ BehaviorGuard — Behavioral Risk Intelligence Platform

BehaviorGuard is an end-to-end **behavioral risk detection and moderation intelligence platform** designed to identify spam, coordinated campaigns, and abnormal user behavior using **explainable risk scoring**.

The system combines a **Python ML backend (FastAPI)** with a **.NET 8 MVC dashboard** to provide moderators with transparent, actionable insights rather than black-box flags.

---

## 🚀 Features

### 🔍 Behavioral Risk Detection
- Post-level and account-level risk scoring
- Detection of:
  - Coordinated posting behavior
  - Copy-paste / near-duplicate content
  - Burst activity patterns
  - New account anomalies

### 🧠 Unsupervised Pattern Discovery
- Behavioral clustering using **HDBSCAN**
- Automatic grouping of similar posting behaviors
- Cluster confidence estimation

### 🧾 Explainable AI (XAI)
- Each flagged item includes:
  - Top contributing signals
  - Human-readable explanations
  - Confidence score
  - Risk interpretation label (e.g. *Coordinated Campaign*, *Copy-Paste Repetition*)

### 📊 Moderation Dashboard (ASP.NET Core)
- KPI overview (total posts, auto-actions, queued reviews)
- Account-level risk aggregation
- Cluster-level analytics
- Secure authentication with role-based access

---

## 🏗️ Architecture Overview

Browser
│
▼
ASP.NET Core MVC Dashboard (.NET 8)
│
▼
FastAPI Backend (Python)
│
▼
Behavioral Risk Engine
├── Feature Extraction
├── Similarity & Coordination Analysis
├── Behavioral Clustering
├── Risk Scoring
└── Explainability Layer

yaml
Copier le code

---

## 🧩 Backend Stack (Python)

- **FastAPI** — REST API
- **Pandas / NumPy** — data processing
- **scikit-learn** — clustering & similarity
- **Sentence Embeddings** — semantic similarity
- **HDBSCAN** — unsupervised behavior discovery

### Key API Endpoints

| Endpoint | Method | Description |
|-------|------|------------|
| `/api/health` | GET | Health check |
| `/api/dashboard` | GET | Current moderation snapshot |
| `/api/upload-cv` | POST | Upload dataset & recompute risks |

---

## 🖥️ Frontend Stack (.NET)

- **ASP.NET Core MVC (.NET 8)**
- **Bootstrap 5 + Bootstrap Icons**
- **Chart.js** for visual analytics
- Cookie-based authentication
- Custom authorization flow with access-denied handling

---

## 🔐 Authentication & Access Control

- Users must be authenticated to access the dashboard
- Unauthorized access redirects to a dedicated **Access Restricted** page
- Role support (Admin / Moderator) for future extensions

---

## 📁 Project Structure (Simplified)

api/
├── main.py
├── requirements.txt
└── runtime.txt

engine/
├── pipeline/
├── models/
├── detectors/
├── explain/
└── utils/

UI/
└── Behavior-risk-UI/
├── Controllers/
├── Views/
├── Services/
└── wwwroot/

yaml
Copier le code

---

## ⚙️ Deployment Notes

- Designed for **CPU-only environments**
- Handles large ML dependencies
- Supports experimental Python 3.13 setups
- Can be deployed as two independent services:
  - FastAPI backend
  - ASP.NET MVC frontend

---

## 🧠 Design Philosophy

> Moderation systems should **explain** before they **enforce**.

BehaviorGuard prioritizes:
- Transparency over black-box decisions
- Human-in-the-loop moderation
- Scalable, modular architecture
- Real-world deployment constraints

---

## 📌 Current Status

**Version:** 2.0 (MVP+)  
- Risk weights are currently static  
- Behavioral clustering is active  
- Designed to evolve toward adaptive / learned weighting

---

## 📬 Author

Developed by **Mohanned**  
Software Engineering • AI • Systems Design

Feel free to reach out for collaboration, feedback, or deployment discussions.