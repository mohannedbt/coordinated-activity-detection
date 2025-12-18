import re
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
