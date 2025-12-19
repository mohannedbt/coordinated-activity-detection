import matplotlib.pyplot as plt
import pandas as pd
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