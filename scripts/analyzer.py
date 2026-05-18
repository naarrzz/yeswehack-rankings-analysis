"""
Analysis: 5 observations from hunters_full.csv.

Statistical methods:
  - Power-law fit (log-log regression) and Gini coefficient for points concentration
  - Spearman rank correlation (non-parametric) for impact vs reports and seniority vs points
  - Mann-Whitney U test (non-parametric) for public vs private profile comparison

Libraries: pandas, numpy, scipy, matplotlib
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu, spearmanr


def gini(v):
    """Compute Gini coefficient: 0 = perfect equality, 1 = winner-takes-all."""
    s = np.sort(v)
    n = len(s)
    c = np.cumsum(s)
    return ((2 * np.sum(np.arange(1, n + 1) * s)) - (n + 1) * c[-1]) / (n * c[-1])


def main():
    df = pd.read_csv("hunters_full.csv")

    print("=" * 60)
    print("Observation 1: Points concentration (power law)")
    print("=" * 60)
    total = df["points"].sum()
    for n in (1, 10, 25, 50):
        pct = df.nlargest(n, "points")["points"].sum() / total * 100
        print(f"  Top {n:>3}: {pct:.1f}%")
    print(f"  Gini coefficient: {gini(df['points'].values):.3f}")
    slope, intercept = np.polyfit(np.log(df["rank"]), np.log(df["points"]), 1)
    print(f"  Power-law fit: log(points) = {intercept:.2f} + {slope:.2f} * log(rank)")
    print(f"  Exponent alpha = {-slope:.2f}")

    print()
    print("=" * 60)
    print("Observation 2: Nationality distribution")
    print("=" * 60)
    print(df["nationality"].value_counts().head(10).to_string())

    print()
    print("=" * 60)
    print("Observation 3: Impact vs reports (Spearman)")
    print("=" * 60)
    valid = df.dropna(subset=["impact", "nb_reports"])
    rho, p = spearmanr(valid["impact"], valid["nb_reports"])
    print(f"  Spearman rho = {rho:.3f}, p = {p:.4f}")
    df["impact_per_report"] = df["impact"] / df["nb_reports"]
    print("  Top 5 impact-per-report (quality strategy):")
    top5 = df.nlargest(5, "impact_per_report")[
        ["username", "rank", "impact", "nb_reports", "impact_per_report"]
    ]
    print(top5.to_string(index=False))

    print()
    print("=" * 60)
    print("Observation 4: Seniority vs points")
    print("=" * 60)
    df["joined_year"] = pd.to_numeric(df["joined_on"], errors="coerce")
    yr = df.dropna(subset=["joined_year"])
    rho_yr, p_yr = spearmanr(yr["joined_year"], yr["points"])
    print(f"  Seniority rho = {rho_yr:.3f}, p = {p_yr:.4f}")
    print(yr.groupby("joined_year")["points"].agg(["count", "mean"]).round(0).to_string())

    print()
    print("=" * 60)
    print("Observation 5: Public vs private profile (Mann-Whitney U)")
    print("=" * 60)
    pub  = df[df["is_public"]]["points"]
    priv = df[~df["is_public"]]["points"]
    u, p_mw = mannwhitneyu(pub, priv, alternative="two-sided")
    print(f"  Public:  n={len(pub):>3}, median={pub.median():.0f}, mean={pub.mean():.0f}")
    print(f"  Private: n={len(priv):>3}, median={priv.median():.0f}, mean={priv.mean():.0f}")
    print(f"  Mann-Whitney U = {u:.0f}, p = {p_mw:.3f}")


if __name__ == "__main__":
    main()
