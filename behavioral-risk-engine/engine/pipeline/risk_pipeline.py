import pandas as pd
from typing import Dict, Any

from engine.detectors.copy_paste import detect_duplicates
from engine.detectors.frequent_posting import detect_coordinated_posts
from engine.detectors.bot_rating import score_accounts
from engine.utils.preprocessing import preprocess
from engine.utils.preprocessing import assign_narrative
from engine.features.post_features import PostFeatureExtractor
from engine.models.behavior_clustering import BehaviorClusterer



class RiskPipeline:
    """
    Behavioral Risk Detection Pipeline

    Stages:
        1. Preprocessing
        2. Signal detection
        3. Feature extraction
        4. Risk fusion (heuristic for now)
        5. Aggregation
    """

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = config or {}
        self.feature_extractor = PostFeatureExtractor()
        self.clusterer = BehaviorClusterer(
            min_cluster_size=self.config.get("min_cluster_size", 5)
        )

    # --------------------------------------------------
    # Stage 1: Preprocessing
    # --------------------------------------------------


    def preprocess_posts(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        required = {
            "post_id",
            "text",
            "timestamp",
            "account_id",
            "account_age_days",
        }

        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Normalize types
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Text preprocessing
        df["clean_text"] = df["text"].apply(preprocess)

        # Narrative assignment (🔥 this fixes your error)
        df["narrative"] = df["text"].apply(assign_narrative)

        return df

    # --------------------------------------------------
    # Stage 2: Signal Detection
    # --------------------------------------------------
    def detect_signals(self, df: pd.DataFrame) -> Dict[str, Any]:
        (
            duplicate_post_ids,
            similarity_matrix,
            clusters_df
        ) = detect_duplicates(df)

        (
            coordinated_post_ids,
            coordination_events
        ) = detect_coordinated_posts(df)

        account_scores = score_accounts(
            df_posts=df,
            duplicate_post_ids=duplicate_post_ids,
            coordinated_post_ids=coordinated_post_ids,
        )

        return {
            "duplicate_post_ids": duplicate_post_ids,
            "coordinated_post_ids": coordinated_post_ids,
            "similarity_matrix": similarity_matrix,
            "clusters": clusters_df,
            "coordination_events": coordination_events,
            "account_scores": account_scores,
        }

    # --------------------------------------------------
    # Stage 3: Feature Extraction
    # --------------------------------------------------
    def extract_features(
        self,
        df: pd.DataFrame,
        signals: Dict[str, Any],
    ) -> tuple[pd.DataFrame, list[str]]:

        df_features, feature_cols = self.feature_extractor.extract(
            df_posts=df,
            similarity_matrix=signals["similarity_matrix"],
            clusters_df=signals["clusters"],
            coordination_events=signals["coordination_events"],
        )


        return df_features, feature_cols

    # --------------------------------------------------
    # Stage 4: Risk Fusion (heuristic placeholder)
    # --------------------------------------------------
    def fuse_risk(
        self,
        df: pd.DataFrame,
        feature_cols: list[str],
    ) -> pd.DataFrame:

        weights = {
            "sim_max": 0.30,
            "sim_mean": 0.10,
            "cluster_size_norm": 0.25,
            "coordination_score": 0.25,
            "account_age_norm": 0.10,
        }

        df["risk_score"] = 0.0

        for feature, weight in weights.items():
            df["risk_score"] += df[feature] * weight

        # Convert to percentage
        df["risk_score"] = (df["risk_score"] * 100).clip(0, 100)

        return df


    # --------------------------------------------------
    # Stage 5: Aggregation
    # --------------------------------------------------
    def aggregate_account_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby("account_id")
            .agg(
                avg_risk=("risk_score", "mean"),
                max_risk=("risk_score", "max"),
                total_posts=("post_id", "count"),
            )
            .reset_index()
        )

    def aggregate_narrative_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        return (
            df.groupby("narrative")
            .agg(
                avg_risk=("risk_score", "mean"),
                max_risk=("risk_score", "max"),
                suspicious_posts=("risk_score", lambda x: (x >= 70).sum()),
                total_posts=("post_id", "count"),
            )
            .reset_index()
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------
    def run(self, df_posts: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        # Stage 1: preprocessing
        df = self.preprocess_posts(df_posts)

        # Stage 2: signal detection
        signals = self.detect_signals(df)

        # Merge duplicate clusters into df
        df = df.merge(
            signals["clusters"],
            on="post_id",
            how="left"
        )

        # Stage 3: feature extraction
        df, feature_cols = self.extract_features(df, signals)

        # 🔥 NEW: Step 2 — Behavioral clustering
        df = self.clusterer.fit_predict(df, feature_cols)

        # Stage 4: risk fusion (still heuristic)
        df = self.fuse_risk(df, feature_cols)

        # Stage 5: aggregation
        return {
            "posts": df,
            "accounts": self.aggregate_account_risk(df),
            "narratives": self.aggregate_narrative_risk(df),
            "features": feature_cols,
            "signals": signals,
        }

