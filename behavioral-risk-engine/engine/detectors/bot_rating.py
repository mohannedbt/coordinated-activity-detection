import pandas as pd


def score_accounts(
    df_posts: pd.DataFrame,
    duplicate_post_ids: set,
    coordinated_post_ids: set
):
    """
    Score accounts based on behavioral heuristics.

    Parameters
    ----------
    df_posts : pd.DataFrame
        Must contain columns:
        ['post_id', 'account_id', 'timestamp', 'account_age_days']
    duplicate_post_ids : set
        Post IDs involved in duplicate / near-duplicate content
    coordinated_post_ids : set
        Post IDs involved in coordinated temporal bursts

    Returns
    -------
    pd.DataFrame
        One row per account with risk score and flags
    """

    required = {"post_id", "account_id", "timestamp", "account_age_days"}
    if not required.issubset(df_posts.columns):
        raise ValueError(f"df_posts must contain columns: {required}")

    df_posts = df_posts.copy()
    df_posts["timestamp"] = pd.to_datetime(df_posts["timestamp"])

    account_rows = []

    for account_id, group in df_posts.groupby("account_id"):
        score = 0
        flags = []

        # Rule 1: Young account
        if group["account_age_days"].iloc[0] < 30:
            score += 30
            flags.append("young_account")

        # Rule 2: High posting rate
        duration_hours = max(
            (group["timestamp"].max() - group["timestamp"].min()).total_seconds() / 3600,
            1
        )
        posting_rate = len(group) / duration_hours
        if posting_rate > 5:
            score += 30
            flags.append("high_posting_rate")

        # Rule 3: Duplicate content
        if set(group["post_id"]).intersection(duplicate_post_ids):
            score += 20
            flags.append("duplicate_content")

        # Rule 4: Coordinated bursts
        if set(group["post_id"]).intersection(coordinated_post_ids):
            score += 20
            flags.append("coordinated_activity")

        account_rows.append({
            "account_id": account_id,
            "bot_score": min(score, 100),
            "suspicious": score >= 70,
            "flags": flags
        })

    return pd.DataFrame(account_rows)
