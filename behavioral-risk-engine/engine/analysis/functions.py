import pandas as pd
# --------------------------------------------------
# ANALYSIS HELPERS (NO TOP-K BIAS)
# --------------------------------------------------

def print_risk_summary(df, name="ALL POSTS"):
    print(f"\n=== RISK DISTRIBUTION: {name} ===")
    print(df["risk_score"].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95]))

    print("\nConfidence distribution:")
    print(df["confidence"].describe(percentiles=[0.25, 0.5, 0.75, 0.9]))

    print("\nReason categories:")
    print(df["reason_category"].value_counts(normalize=True))


def risk_conf_matrix(df, risk_thr=70, conf_thr=0.7):
    high_risk = df["risk_score"] >= risk_thr
    high_conf = df["confidence"] >= conf_thr

    table = pd.crosstab(
        high_risk,
        high_conf,
        rownames=["High risk"],
        colnames=["High confidence"]
    )

    print("\n=== RISK × CONFIDENCE MATRIX ===")
    print(table)


def scenario_report(df):
    if "scenario" not in df.columns:
        print("\n(no scenario column found — skipping scenario report)")
        return

    print("\n=== SCENARIO REPORT ===")
    for name, g in df.groupby("scenario"):
        print(f"\n--- {name.upper()} ---")
        print(f"Avg risk: {g['risk_score'].mean():.2f}")
        print(f"High risk %: {(g['risk_score'] >= 70).mean():.2%}")
        print(f"High confidence %: {(g['confidence'] >= 0.7).mean():.2%}")
        print("Reason categories:")
        print(g["reason_category"].value_counts(normalize=True))


def inspect_band(df, low, high, max_rows=8):
    band = df[(df["risk_score"] >= low) & (df["risk_score"] < high)]
    print(f"\n=== POSTS WITH RISK IN [{low}, {high}) (n={len(band)}) ===")
    if band.empty:
        print("None")
        return

    cols = ["post_id", "text", "risk_score", "confidence", "reason_category"]
    print(band[cols].head(max_rows))