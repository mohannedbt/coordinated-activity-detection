import pandas as pd
from engine.pipeline.risk_pipeline import RiskPipeline
from engine.utils.functions import decision_policy, compute_account_ewma
from engine.utils.functions import (
    serialize_posts,serialize_accounts 
    )
def run_mvp_pipeline(url="data/sample_posts.csv") -> dict:
    df_posts = pd.read_csv(url)

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
    object={
        "summary": {
            "total_posts": len(posts),
            "auto_actions": int((posts.decision == "AUTO_ACTION").sum()),
            "queue_review": int((posts.decision == "QUEUE_REVIEW").sum()),
        },
        "posts": serialize_posts(posts),
        "accounts": serialize_accounts(account_view),
        "clusters": serialize_accounts(cluster_view),
    }
    print(object)

    return object