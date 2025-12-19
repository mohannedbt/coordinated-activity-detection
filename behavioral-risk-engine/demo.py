import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from engine.pipeline.risk_pipeline import RiskPipeline


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
# Visualization helpers (ANALYST UI)
# --------------------------------------------------

def plot_similarity_vs_coordination(df, path):
    plt.figure(figsize=(8, 6))
    sc = plt.scatter(
        df["sim_mean"],
        df["coordination_score"],
        c=df["behavior_cluster"],
        cmap="tab10",
        alpha=0.8,
        edgecolors="k"
    )
    plt.axhline(0.5, linestyle="--", alpha=0.4)
    plt.axvline(0.5, linestyle="--", alpha=0.4)
    plt.xlabel("Mean content similarity")
    plt.ylabel("Coordination score")
    plt.title("Behavior map: Similarity vs Coordination")
    plt.colorbar(sc, label="Behavior cluster")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def plot_cluster_size_vs_account_age(df, path):
    plt.figure(figsize=(8, 6))
    sc = plt.scatter(
        df["cluster_size"],
        df["account_age_days"],
        c=df["behavior_cluster"],
        cmap="tab10",
        alpha=0.8,
        edgecolors="k"
    )
    plt.xlabel("Copy-paste cluster size")
    plt.ylabel("Account age (days)")
    plt.title("Behavior map: Repetition vs Account Age")
    plt.colorbar(sc, label="Behavior cluster")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


def plot_similarity_vs_cluster_size(df, path):
    plt.figure(figsize=(8, 6))
    sc = plt.scatter(
        df["sim_mean"],
        df["cluster_size"],
        c=df["behavior_cluster"],
        cmap="tab10",
        alpha=0.8,
        edgecolors="k"
    )
    plt.xlabel("Mean content similarity")
    plt.ylabel("Cluster size")
    plt.title("Behavior map: Similarity vs Repetition")
    plt.colorbar(sc, label="Behavior cluster")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()


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


# --------------------------------------------------
# MAIN DEMO (Analyst Console UI)
# --------------------------------------------------

def main():
    os.makedirs("outputs", exist_ok=True)

    print("\nGenerating demo data...")
    # df_posts = generate_demo_posts() # Use this to generate semi-realistic demo data
    df_posts = pd.read_csv("data/sample_posts.csv") # Or load from CSV

    pipeline = RiskPipeline()

    print("Running risk pipeline...")
    results = pipeline.run(df_posts)
    posts = results["posts"]

    # --------------------------------------------------
    # TOP POSTS
    # --------------------------------------------------

    print("\n=== TOP RISKY POSTS ===")
    top = posts.sort_values("risk_score", ascending=False).head(10)
    print(top[[
        "post_id",
        "text",
        "risk_score",
        "confidence",
        "behavior_cluster"
    ]])

    # --------------------------------------------------
    # CLUSTER SUMMARY
    # --------------------------------------------------

    print("\n=== BEHAVIORAL CLUSTERS ===")
    clusters = (
        posts.groupby("behavior_cluster")
        .agg(
            posts=("post_id", "count"),
            avg_risk=("risk_score", "mean"),
            avg_sim=("sim_mean", "mean"),
            avg_coord=("coordination_score", "mean"),
            avg_account_age=("account_age_days", "mean"),
        )
    )
    print(clusters)

    print("\n=== CLUSTER INTERPRETATION ===")
    for cid, grp in posts.groupby("behavior_cluster"):
        if cid == -1:
            print(f"Cluster -1: Outliers / rare behavior ({len(grp)} posts)")
        else:
            print(
                f"Cluster {cid}: {len(grp)} posts | "
                f"avg_sim={grp['sim_mean'].mean():.2f} | "
                f"avg_coord={grp['coordination_score'].mean():.2f}"
            )

    # --------------------------------------------------
    # VISUAL MAPS (Step 3 intuition)
    # --------------------------------------------------

    plot_similarity_vs_coordination(posts, "outputs/01_similarity_vs_coordination.png")
    plot_cluster_size_vs_account_age(posts, "outputs/02_cluster_size_vs_account_age.png")
    plot_similarity_vs_cluster_size(posts, "outputs/03_similarity_vs_cluster_size.png")

    print("\nBehavior maps saved to ./outputs/")

    # --------------------------------------------------
    # EXPLANATIONS (Step 4)
    # --------------------------------------------------

    print("\n=== TOP 5 POSTS WITH EXPLANATIONS ===")
    for _, r in top.head(5).iterrows():
        label = risk_label(r["risk_score"], r["confidence"])
        print(f"\nPost {int(r['post_id'])} | risk={r['risk_score']:.2f} | conf={r['confidence']:.2f}")
        print("Interpretation:", label)
        print("Text:", r["text"])
        print("Top drivers:", r["top_drivers"])
        print("Why flagged:")
        print("This post matches a behavioral pattern involving repetition and/or coordination.")
        for line in r["explanations"]:
            print(" -", line)


# --------------------------------------------------
if __name__ == "__main__":
    main()
