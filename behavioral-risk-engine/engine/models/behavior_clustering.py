import pandas as pd
import numpy as np
import hdbscan
from sklearn.preprocessing import StandardScaler


class BehaviorClusterer:
    """
    Step 2: Unsupervised behavioral pattern discovery
    """

    def __init__(self, min_cluster_size: int = 2): # Adjusted default for testing (Real default 5)
        self.scaler = StandardScaler()
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            metric="euclidean",
            prediction_data=True
        )

    def fit_predict(
        self,
        df: pd.DataFrame,
        feature_cols: list[str]
    ) -> pd.DataFrame:

        X = df[feature_cols].values
        X_scaled = self.scaler.fit_transform(X)

        labels = self.clusterer.fit_predict(X_scaled)
        probs = self.clusterer.probabilities_

        df = df.copy()
        df["behavior_cluster"] = labels
        df["cluster_confidence"] = np.where(labels == -1, 0.0, probs)

        return df
