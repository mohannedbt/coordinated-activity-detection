import os
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta

from engine.pipeline.risk_pipeline import RiskPipeline
from engine.visualization.functions import (
    plot_similarity_vs_coordination,
    plot_cluster_size_vs_account_age,
    plot_similarity_vs_cluster_size,
)
from engine.analysis.functions import (
    print_risk_summary,
    risk_conf_matrix,
)   
from engine.utils.functions import compute_account_ewma
# --------------------------------------------------
# Interpretation helpers (UI logic only)
# --------------------------------------------------

def risk_label(risk, conf):
    if risk >= 70 and conf >= 0.7:
        return "🚨 Strong coordinated behavior"
    if risk >= 70 and conf < 0.7:
        return "⚠️ Suspicious pattern (low confidence)"
    if risk >= 40:
        return "🧐 Mild anomaly"
    return "ℹ️ Likely benign"





# --------------------------------------------------
# Demo data generator (semi-realistic, NOT random noise)
# --------------------------------------------------

def generate_demo_posts():
    base = datetime.now()
    posts = []
    pid = 0

    # Normal long-term users
    for i in range(8):
        posts.append({
            "post_id": pid,
            "text": f"Just sharing a normal thought {i}",
            "timestamp": base + timedelta(minutes=i * 7),
            "account_id": f"user_normal_{i}",
            "account_age_days": 400,
        })
        pid += 1

    # Copy-paste crypto hype
    for i in range(5):
        posts.append({
            "post_id": pid,
            "text": "Seeing strong momentum on Dogecoin today",
            "timestamp": base + timedelta(minutes=30 + i),
            "account_id": f"user_spam_{i % 2}",
            "account_age_days": 25,
        })
        pid += 1

    # Coordinated burst
    for i in range(3):
        posts.append({
            "post_id": pid,
            "text": "Dogecoin might be the next big move",
            "timestamp": base + timedelta(minutes=90),
            "account_id": f"user_burst_{i}",
            "account_age_days": 15,
        })
        pid += 1

    # Legit repetition (older accounts)
    for i in range(6):
        posts.append({
            "post_id": pid,
            "text": "Reading a book",
            "timestamp": base + timedelta(minutes=150 + i * 10),
            "account_id": f"user_old_{i}",
            "account_age_days": 600,
        })
        pid += 1

    return pd.DataFrame(posts)
def run_mvp_pipeline() -> dict:
    df_posts = pd.read_csv("data/sample_posts.csv")

    pipeline = RiskPipeline()
    results = pipeline.run(df_posts)

    posts = results["posts"].copy()

    posts["decision"] = posts.apply(
        lambda r: decision_policy(r["risk_score"], r["confidence"]),
        axis=1
    )

    posts = compute_account_ewma(posts, alpha=0.3)

    account_view = (
        posts.groupby("account_id")
        .agg(
            avg_risk=("risk_score", "mean"),
            max_risk=("risk_score", "max"),
            avg_confidence=("confidence", "mean"),
            risk_trend=("risk_ewma", "last"),
            total_posts=("post_id", "count"),
        )
        .reset_index()
        .sort_values("max_risk", ascending=False)
    )

    cluster_view = (
        posts.groupby("behavior_cluster")
        .agg(
            posts=("post_id", "count"),
            avg_risk=("risk_score", "mean"),
            avg_confidence=("confidence", "mean"),
            auto_actions=("decision", lambda x: (x == "AUTO_ACTION").sum()),
        )
        .reset_index()
    )

    return {
        "summary": {
            "total_posts": len(posts),
            "auto_actions": int((posts.decision == "AUTO_ACTION").sum()),
            "queue_review": int((posts.decision == "QUEUE_REVIEW").sum()),
        },
        "posts": serialize_posts(posts),
        "accounts": serialize_accounts(account_view),
        "clusters": serialize_accounts(cluster_view),
    }


# --------------------------------------------------
# Configuration (easy to move to env / config file)
# --------------------------------------------------

RISK_AUTO = 75
CONF_AUTO = 0.8

RISK_REVIEW = 50
CONF_REVIEW = 0.5

OUTPUT_DIR = "outputs"


# --------------------------------------------------
# Decision policy (WEB-READY)
# --------------------------------------------------

def decision_policy(risk: float, confidence: float) -> str:
    if risk >= RISK_AUTO and confidence >= CONF_AUTO:
        return "AUTO_ACTION"
    if risk >= RISK_REVIEW and confidence >= CONF_REVIEW:
        return "QUEUE_REVIEW"
    return "NO_ACTION"


# --------------------------------------------------
# Serialization helpers (WEB)
# --------------------------------------------------

def serialize_posts(df: pd.DataFrame) -> list[dict]:
    """Convert posts dataframe into JSON-safe records."""
    cols = [
        "post_id",
        "text",
        "account_id",
        "risk_score",
        "confidence",
        "decision",
        "reason_category",
        "top_drivers",
        "explanations",
    ]
    return df[cols].to_dict(orient="records")


def serialize_accounts(df: pd.DataFrame) -> list[dict]:
    return df.to_dict(orient="records")


# --------------------------------------------------
# MAIN (CLI + WEB-READY)
# --------------------------------------------------

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\nRunning behavioral risk MVP...\n")

    # --------------------------------------------------
    # Load data (CSV today, API tomorrow)
    # --------------------------------------------------
    df_posts = pd.read_csv("data/sample_posts.csv")

    # --------------------------------------------------
    # Run pipeline
    # --------------------------------------------------
    pipeline = RiskPipeline()
    results = pipeline.run(df_posts)

    posts = results["posts"].copy()

    # --------------------------------------------------
    # Semantics (explicit)
    # --------------------------------------------------
    print("=== SEMANTICS ===")
    print("Risk       → severity of behavior")
    print("Confidence → certainty pattern is real\n")

    # --------------------------------------------------
    # Decisions
    # --------------------------------------------------
    posts["decision"] = posts.apply(
        lambda r: decision_policy(r["risk_score"], r["confidence"]),
        axis=1
    )

    print("=== DECISION POLICY ===")
    print("AUTO_ACTION  → risk ≥ 75 AND confidence ≥ 0.8")
    print("QUEUE_REVIEW → risk ≥ 50 AND confidence ≥ 0.5")
    print("NO_ACTION    → otherwise\n")

    print("=== DECISION SUMMARY ===")
    print(posts["decision"].value_counts(), "\n")

    # --------------------------------------------------
    # Actionable posts (NO top-k bias)
    # --------------------------------------------------
    actionable = posts[posts["decision"] != "NO_ACTION"] \
        .sort_values("risk_score", ascending=False)

    print("=== ACTIONABLE POSTS ===")
    for _, r in actionable.iterrows():
        print(
            f"\nPost {int(r.post_id)}"
            f" | risk={r.risk_score:.2f}"
            f" | conf={r.confidence:.2f}"
            f" | decision={r.decision}"
        )
        print("Interpretation:", risk_label(r.risk_score, r.confidence))
        print("Text:", r.text)
        for line in r.explanations:
            print(" -", line)

    # --------------------------------------------------
    # Temporal smoothing (EWMA)
    # --------------------------------------------------
    posts = compute_account_ewma(posts, alpha=0.3)

    # --------------------------------------------------
    # Aggregations (WEB-READY)
    # --------------------------------------------------
    account_view = (
        posts.groupby("account_id")
        .agg(
            avg_risk=("risk_score", "mean"),
            max_risk=("risk_score", "max"),
            avg_confidence=("confidence", "mean"),
            risk_trend=("risk_ewma", "last"),
            total_posts=("post_id", "count"),
        )
        .reset_index()
        .sort_values("max_risk", ascending=False)
    )

    cluster_view = (
        posts.groupby("behavior_cluster")
        .agg(
            posts=("post_id", "count"),
            avg_risk=("risk_score", "mean"),
            avg_confidence=("confidence", "mean"),
            auto_actions=("decision", lambda x: (x == "AUTO_ACTION").sum()),
        )
        .reset_index()
    )

    # --------------------------------------------------
    # Analysis (debug / analyst)
    # --------------------------------------------------
    print_risk_summary(posts)
    risk_conf_matrix(posts)

    # --------------------------------------------------
    # Visualizations (saved for web)
    # --------------------------------------------------
    plot_similarity_vs_coordination(
        posts, f"{OUTPUT_DIR}/01_similarity_vs_coordination.png"
    )
    plot_cluster_size_vs_account_age(
        posts, f"{OUTPUT_DIR}/02_cluster_size_vs_account_age.png"
    )
    plot_similarity_vs_cluster_size(
        posts, f"{OUTPUT_DIR}/03_similarity_vs_cluster_size.png"
    )

    print("\nBehavior maps saved to ./outputs/")

    # --------------------------------------------------
    # FINAL WEB PAYLOAD (MVP)
    # --------------------------------------------------
    web_payload = {
        "summary": {
            "total_posts": len(posts),
            "auto_actions": int((posts.decision == "AUTO_ACTION").sum()),
            "queue_review": int((posts.decision == "QUEUE_REVIEW").sum()),
        },
        "posts": serialize_posts(posts),
        "accounts": serialize_accounts(account_view),
        "clusters": serialize_accounts(cluster_view),
    }

    with open(f"{OUTPUT_DIR}/mvp_payload.json", "w", encoding="utf-8") as f:
        json.dump(web_payload, f, indent=2, ensure_ascii=False)

    print("\n✅ MVP payload exported to outputs/mvp_payload.json")
    print("\n=== NEXT STEPS ===")
    print("• Plug this payload into a web UI")
    print("• Wrap main() in FastAPI endpoint")
    print("• Add rolling alerts / thresholds")


# --------------------------------------------------
if __name__ == "__main__":
    main()