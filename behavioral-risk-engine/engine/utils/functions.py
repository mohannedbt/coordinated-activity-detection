import re
import pandas as pd
# Text Preprocessing
def preprocess(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)  # remove URLs
    text = re.sub(r"[^a-z0-9\s#\$]", "", text)  # keep hashtags and $ signs
    return text
import re

def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-z0-9\s#\$]", "", text)
    return text.strip()

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
def assign_narrative(text: str) -> str:
    """
    Assigns a narrative label to a post based on keyword heuristics.
    """

    text = text.lower()

    if "$btc" in text or "bitcoin" in text:
        return "BTC"

    if "$eth" in text or "ethereum" in text:
        return "ETH"

    if "$doge" in text or "dogecoin" in text:
        return "DOGE"

    return "OTHER"
def compute_account_ewma(df, alpha=0.3):
    df = df.sort_values("timestamp")
    df["risk_ewma"] = (
        df.groupby("account_id")["risk_score"]
          .apply(lambda x: x.ewm(alpha=alpha, adjust=False).mean())
          .reset_index(level=0, drop=True)
    )
    return df
RISK_AUTO = 75
CONF_AUTO = 0.8

RISK_REVIEW = 50
CONF_REVIEW = 0.5
def decision_policy(risk: float, confidence: float) -> str:
    if risk >= RISK_AUTO and confidence >= CONF_AUTO:
        return "AUTO_ACTION"
    if risk >= RISK_REVIEW and confidence >= CONF_REVIEW:
        return "QUEUE_REVIEW"
    return "NO_ACTION"
