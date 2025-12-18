import pandas as pd


def detect_coordinated_posts(
    df: pd.DataFrame,
    window: str = "10min",
    min_posts: int = 3
):
    """
    Detect coordinated posting bursts based on temporal activity.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: ['post_id', 'timestamp', 'narrative']
    window : str
        Pandas resampling window (e.g. '5min', '10min')
    min_posts : int
        Minimum number of posts in a window to consider a burst

    Returns
    -------
    coordinated_post_ids : set
        Set of post_ids involved in coordinated bursts
    events : list of dict
        Metadata about each detected burst
    """

    if not {"post_id", "timestamp", "narrative"}.issubset(df.columns):
        raise ValueError("DataFrame must contain post_id, timestamp, narrative")

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    coordinated_post_ids = set()
    events = []

    for narrative, group in df.groupby("narrative"):
        if narrative == "OTHER":
            continue

        time_counts = (
            group.set_index("timestamp")
            .resample(window)
            .size()
        )

        spike_windows = time_counts[time_counts >= min_posts]

        for window_start, count in spike_windows.items():
            window_end = window_start + pd.Timedelta(window)

            window_posts = group[
                (group["timestamp"] >= window_start) &
                (group["timestamp"] < window_end)
            ]

            post_ids = window_posts["post_id"].tolist()

            coordinated_post_ids.update(post_ids)

            events.append({
                "narrative": narrative,
                "window_start": window_start,
                "window_end": window_end,
                "num_posts": len(post_ids),
                "post_ids": post_ids
            })

    return coordinated_post_ids, events
