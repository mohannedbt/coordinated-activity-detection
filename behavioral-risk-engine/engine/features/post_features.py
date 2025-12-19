import pandas as pd
import numpy as np


class PostFeatureExtractor:
    """
    Transforms raw detection signals into normalized numerical feature vectors.
    """

    @staticmethod
    def _safe_norm(col: pd.Series) -> pd.Series:
        max_val = col.max()
        if max_val <= 0 or pd.isna(max_val):
            return col * 0.0
        return col / max_val

    def extract(
        self,
        df_posts: pd.DataFrame,
        similarity_matrix,
        clusters_df: pd.DataFrame,
        coordination_events: list,
    ):

        df = df_posts.copy()

        # ---------------------------------------------------------------------------
        # Content similarity features (already [0,1]) + removing the self-similarity
        # ---------------------------------------------------------------------------
        sim = similarity_matrix.copy() 
        np.fill_diagonal(sim, 0.0)   # or -np.inf for max, but 0 works since similarities are >=0

        df["sim_max"] = sim.max(axis=1)
        df["sim_mean"] = sim.mean(axis=1)

        # --------------------------------------------------
        # Cluster features
        # --------------------------------------------------
        cluster_sizes = clusters_df.groupby("cluster_id").size()
        df["cluster_size"] = df["cluster_id"].map(cluster_sizes).fillna(1)

        df["cluster_size_norm"] = self._safe_norm(df["cluster_size"])

        # --------------------------------------------------
        # Coordination features
        # --------------------------------------------------
        burst_map = {}
        for event in coordination_events:
            for pid in event["post_ids"]:
                burst_map[pid] = event["num_posts"]

        df["burst_size"] = df["post_id"].map(burst_map).fillna(0)
        df["burst_size_norm"] = self._safe_norm(df["burst_size"])

        df["coordination_score"] = df["burst_size_norm"]

        # --------------------------------------------------
        # Account features
        # --------------------------------------------------
        # Younger accounts = more risky
        df["account_age_norm"] = 1.0 - self._safe_norm(df["account_age_days"])

        # --------------------------------------------------
        # Final feature set (ONLY normalized features)
        # --------------------------------------------------
        feature_cols = [
            "sim_max",
            "sim_mean",
            "cluster_size_norm",
            "coordination_score",
            "account_age_norm",
        ]

        df[feature_cols] = df[feature_cols].fillna(0.0)

        return df, feature_cols
