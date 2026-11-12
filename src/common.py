"""Shared paths + helpers. Everyone imports this; change only with team agreement."""
from pathlib import Path
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "nfhs5_NIEnarya.csv"
CLEAN = ROOT / "data" / "processed" / "nfhs5_clean.csv"
FEATURES = ROOT / "data" / "processed" / "nfhs5_features.csv"
DISTRICT = ROOT / "data" / "processed" / "district_profile.csv"
FIG = ROOT / "reports" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid")

def save(name):
    plt.tight_layout(); plt.savefig(FIG / f"{name}.png", dpi=130); plt.close()

def wmean(g, col):
    """Survey-weighted % (always use for national / group prevalence)."""
    m = g[col].notna()
    return np.average(g.loc[m, col], weights=g.loc[m, "sample_wt"]) * 100 if m.any() else np.nan

def prev(df, by, col="stunted"):
    return df.groupby(by, observed=True).apply(lambda g: wmean(g, col), include_groups=False)
