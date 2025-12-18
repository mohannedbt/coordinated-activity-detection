import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from engine.pipeline.risk_pipeline import RiskPipeline


# --------------------------------------------------
# Visualization helpers (DEMO ONLY)
# --------------------------------------------------

def plot_similarity_vs_coordination(df, output_path):
    plt.figure(figsize=(8, 6))

    scatter = plt.scatter(
        df["sim_mean"],
        df["coordination_score"],
        c=df["behavior_cluster"],
        cmap="tab10",
        alpha=0.8,
        edgecolors="k"
    )

    plt.xlabel("Mean Content Similarity (sim_mean)")
    plt.ylabel("Coordination Score")
    plt.title("Behavior Map: Similarity vs Coordination")
    plt.colorbar(scatter, label="Behavior Cluster")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_cluster_size_vs_account_age(df, output_path):
    plt.figure(figsize=(8, 6))

    scatter = plt.scatter(
        df["cluster_size"],
        df["account_age_days"],
        c=df["behavior_cluster"],
        cmap="tab10",
        alpha=0.8,
        edgecolors="k"
    )

    plt.xlabel("Copy-Paste Cluster Size")
    plt.ylabel("Account Age (days)")
    plt.title("Behavior Map: Repetition vs Account Age")
    plt.colorbar(scatter, label="Behavior Cluster")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_similarity_vs_cluster_size(df, output_path):
    plt.figure(figsize=(8, 6))

    scatter = plt.scatter(
        df["sim_mean"],
        df["cluster_size"],
        c=df["behavior_cluster"],
        cmap="tab10",
        alpha=0.8,
        edgecolors="k"
    )

    plt.xlabel("Mean Content Similarity (sim_mean)")
    plt.ylabel("Cluster Size")
    plt.title("Behavior Map: Similarity vs Repetition")
    plt.colorbar(scatter, label="Behavior Cluster")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


# --------------------------------------------------
# Demo data generator
# --------------------------------------------------

def generate_demo_posts(n_posts: int = 40) -> pd.DataFrame:
    np.random.seed(42)

    texts = [
        "🚀 Buy $BTC now!",
        "Huge gains incoming $ETH",
        "Invest in $DOGE now!",
        "Normal weather today",
        "Reading a book",
    ]

    posts = []
    start_time = datetime.now()

    for i in range(1, n_posts + 1):
        posts.append({
            "post_id": i,
            "text": np.random.choice(texts),
            "timestamp": start_time + timedelta(minutes=np.random.randint(0, 120)),
            "account_id": f"user_{np.random.randint(1, 11):03d}",
            "account_age_days": np.random.randint(10, 200),
        })

    return pd.DataFrame(posts)


# --------------------------------------------------
# Main demo
# --------------------------------------------------

def main():
    os.makedirs("outputs", exist_ok=True)

    print("\nGenerating demo data...")
    df_posts = generate_demo_posts()

    pipeline = RiskPipeline()

    print("Running risk pipeline...")
    results = pipeline.run(df_posts)

    posts = results["posts"]

    # --------------------------------------------------
    # TEXT OUTPUT
    # --------------------------------------------------

    print("\n=== POST RISK (top 10) ===")
    print(posts.sort_values("risk_score", ascending=False).head(10))

    print("\n=== BEHAVIORAL CLUSTERS ===")
    print(
        posts.groupby("behavior_cluster")
        .agg(
            posts=("post_id", "count"),
            avg_risk=("risk_score", "mean"),
            avg_sim=("sim_mean", "mean"),
            avg_coord=("coordination_score", "mean"),
            avg_account_age=("account_age_days", "mean"),
        )
    )

    print("\n=== OUTLIER POSTS (cluster = -1) ===")
    print(
        posts[posts["behavior_cluster"] == -1][[
            "post_id",
            "text",
            "sim_mean",
            "coordination_score",
            "risk_score"
        ]]
    )

    # --------------------------------------------------
    # VISUALIZATION EXPORT (STEP 3 INTUITION)
    # --------------------------------------------------

    plot_similarity_vs_coordination(
        posts,
        "outputs/01_similarity_vs_coordination.png"
    )

    plot_cluster_size_vs_account_age(
        posts,
        "outputs/02_cluster_size_vs_account_age.png"
    )

    plot_similarity_vs_cluster_size(
        posts,
        "outputs/03_similarity_vs_cluster_size.png"
    )

    print("\nBehavior maps saved to ./outputs/")
    print(" - 01_similarity_vs_coordination.png")
    print(" - 02_cluster_size_vs_account_age.png")
    print(" - 03_similarity_vs_cluster_size.png")


# --------------------------------------------------
if __name__ == "__main__":
    main()
