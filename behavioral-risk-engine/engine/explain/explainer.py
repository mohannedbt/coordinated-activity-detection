from __future__ import annotations
import pandas as pd
from typing import Dict, List


class RiskExplainer:
    """
    Explains risk scores using normalized behavioral signals.
    """

    SIGNAL_THRESHOLDS = {
        "coordination_score": 0.7,
        "sim_max": 0.65,
        "cluster_size_norm": 0.5,
        "account_age_norm": 0.7,
    }

    REASON_LABELS = {
        "coordination": "🚨 Coordinated campaign",
        "copy_paste": "♻️ Copy-paste repetition",
        "new_account": "🆕 New account anomaly",
        "baseline": "🟢 Normal baseline behavior",
    }

    def __init__(self, weights: Dict[str, float]):
        self.weights = weights

        self.labels = {
            "sim_mean": "high average similarity (template-like text)",
            "sim_max": "very high similarity to at least one post (near-duplicate)",
            "cluster_size_norm": "repetition across similar posts",
            "coordination_score": "coordinated timing burst",
            "account_age_norm": "very new account activity",
        }

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------
    def compute_confidence(self, row: pd.Series) -> float:
        active = 0
        strength = 0.0

        for feat, th in self.SIGNAL_THRESHOLDS.items():
            v = row.get(feat, 0.0)
            if v >= th:
                active += 1
                strength += v

        if active == 0:
            return 0.05

        confidence = (
            0.6 * (active / len(self.SIGNAL_THRESHOLDS)) +
            0.4 * (strength / active)
        )
        return round(min(confidence, 1.0), 2)

    # --------------------------------------------------
    # Reason category
    # --------------------------------------------------
    def classify_reason(self, row: pd.Series) -> str:
        if row.get("coordination_score", 0) >= 0.7:
            return "coordination"

        if row.get("sim_max", 0) >= 0.65 and row.get("cluster_size_norm", 0) >= 0.5:
            return "copy_paste"

        if row.get("account_age_norm", 0) >= 0.7:
            return "new_account"

        return "baseline"

    # --------------------------------------------------
    # Main explainer
    # --------------------------------------------------
    def explain_posts(self, df: pd.DataFrame, top_k: int = 4) -> pd.DataFrame:
        df = df.copy()

        explanations = []
        top_drivers = []
        confidences = []
        interpretations = []
        reasons = []

        for _, row in df.iterrows():
            # contributions
            contribs = []
            for feat, w in self.weights.items():
                val = row.get(feat, 0.0)
                contribs.append((feat, val * w))

            contribs.sort(key=lambda x: abs(x[1]), reverse=True)
            drivers = contribs[:top_k]

            exp_lines = []
            driver_feats = []

            for feat, c in drivers:
                label = self.labels.get(feat, feat)
                direction = "increases" if c >= 0 else "decreases"
                exp_lines.append(
                    f"{label} ({feat}={row.get(feat):.3f}) {direction} risk (Δ={c:.2f})"
                )
                driver_feats.append(feat)

            reason = self.classify_reason(row)
            confidence = self.compute_confidence(row)

            explanations.append(exp_lines)
            top_drivers.append(driver_feats)
            confidences.append(confidence)
            reasons.append(reason)
            interpretations.append(self.REASON_LABELS[reason])

        df["explanations"] = explanations
        df["top_drivers"] = top_drivers
        df["confidence"] = confidences
        df["reason_category"] = reasons
        df["interpretation"] = interpretations

        return df
