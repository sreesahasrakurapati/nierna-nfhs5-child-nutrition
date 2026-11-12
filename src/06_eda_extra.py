"""PERSON B - extra EDA: univariate, indicator comparison, confidence intervals, distribution shift,
combined failures, district hot-spots, association strength. Input: nfhs5_features.csv -> charts 12-18"""
from common import *
from scipy.stats import chi2_contingency

df = pd.read_csv(FEATURES)
W = ["Poorest", "Poorer", "Middle", "Richer", "Richest"]
E = ["No education", "Primary", "Secondary", "Higher"]
AG = ["0-5", "6-11", "12-23", "24-35", "36-47", "48-59"]

# ---------------- 1. UNIVARIATE: what does each variable look like? (sample counts, unweighted) ----------------
num = {"age_months": "Age (months)", "weight_kg": "Weight (kg)", "height_cm": "Height (cm)", "birth_weight_g": "Birth weight (g)"}
print("=== Numeric variables ===")
print(df[list(num)].describe().round(1).T[["count", "mean", "50%", "min", "max"]].assign(skew=df[list(num)].skew().round(2)).to_string())
fig, ax = plt.subplots(1, 4, figsize=(16, 3.5))
for a, (c, t) in zip(ax, num.items()):
    sns.histplot(df[c].dropna(), bins=50, ax=a, color="#4C72B0"); a.set_title(t); a.set_xlabel("")
save("12_univariate_numeric")
cats = ["sex", "residence", "wealth_quintile", "mother_edu", "caste"]
fig, ax = plt.subplots(1, 5, figsize=(18, 3.5))
for a, c in zip(ax, cats):
    vc = df[c].value_counts(normalize=True) * 100
    sns.barplot(x=vc.index, y=vc.values, ax=a, color="#55A868"); a.set_title(f"{c} (% of children)"); a.tick_params(axis="x", rotation=40); a.set_xlabel("")
save("13_univariate_categorical")
print("\n=== Category shares (%) ===")
for c in cats: print(c, (df[c].value_counts(normalize=True) * 100).round(1).to_dict())

# ---------------- 2. THREE INDICATORS by wealth ----------------
ind = pd.DataFrame({c: prev(df, "wealth_quintile", c) for c in ["stunted", "wasted", "underweight"]}).reindex(W)
print("\n=== Indicators by wealth (weighted %) ===\n", ind.round(1).to_string())
ind.plot(kind="bar", figsize=(8, 4), color=["#C44E52", "#DD8452", "#4C72B0"]); plt.ylabel("%"); plt.xticks(rotation=0)
plt.title("Stunting, wasting and underweight by wealth"); save("14_indicators_by_wealth")

# ---------------- 3. STATE stunting with approximate 95% confidence intervals ----------------
def p_ci(g, col="stunted"):
    m = g[col].notna(); x, w = g.loc[m, col], g.loc[m, "sample_wt"]
    p = np.average(x, weights=w); neff = w.sum() ** 2 / (w ** 2).sum()   # effective sample size
    return pd.Series({"p": p * 100, "ci": 1.96 * np.sqrt(p * (1 - p) / neff) * 100, "n": int(m.sum())})
st = df.groupby("state").apply(p_ci, include_groups=False).sort_values("p")
print("\n=== Widest state intervals (least certain) ===\n", st.sort_values("ci", ascending=False).head(5).round(1).to_string())
plt.figure(figsize=(7, 9)); plt.barh(st.index, st.p, xerr=st.ci, color="#C44E52", ecolor="black", capsize=2)
plt.xlabel("Weighted stunting % (bars = approx. 95% interval)"); plt.title("State stunting with uncertainty"); save("15_state_stunting_ci")

# ---------------- 4. DISTRIBUTION SHIFT: whole height-for-age curve, not only the < -2 cut-off ----------------
plt.figure(figsize=(8, 4)); sns.boxplot(data=df, x="wealth_quintile", y="haz", order=W, showfliers=False, color="#8172B2")
plt.axhline(-2, color="r", ls="--"); plt.title("Height-for-age z-score by wealth (red line = stunting cut-off)"); save("16_haz_by_wealth")
print("\n=== Median height-for-age z-score by wealth ===\n", df.groupby("wealth_quintile").haz.median().reindex(W).round(2).to_dict())

# ---------------- 5. COMBINED FAILURES: how many children have more than one problem? ----------------
d3 = df.dropna(subset=["stunted", "wasted", "underweight"]).copy()
def combo(r):
    t = [n for n, f in [("Stunted", r.stunted), ("Wasted", r.wasted), ("Underweight", r.underweight)] if f == 1]
    return " + ".join(t) if t else "None"
d3["combo"] = d3[["stunted", "wasted", "underweight"]].apply(combo, axis=1)
cs = d3.groupby("combo").sample_wt.sum() / d3.sample_wt.sum() * 100
cs = cs.sort_values(ascending=False)
print("\n=== Combinations of problems (weighted % of children measured on all three) ===\n", cs.round(1).to_string())
plt.figure(figsize=(7, 4)); sns.barplot(x=cs.values, y=cs.index, color="#937860"); plt.xlabel("% of children"); plt.title("Which problems occur together?"); save("17_failure_combinations")

# ---------------- 6. DISTRICT HOT-SPOTS ----------------
dist = df.groupby(["state", "district_code"]).apply(p_ci, include_groups=False).reset_index()
dist = dist[dist.n >= 100].sort_values("p")
print("\n=== 10 highest-stunting districts (n >= 100) ===\n", dist.tail(10).iloc[::-1].round(1).to_string(index=False))
print("\n=== 10 lowest-stunting districts (n >= 100) ===\n", dist.head(10).round(1).to_string(index=False))
print("\nDistricts analysed:", len(dist), "| range: %.1f%% to %.1f%%" % (dist.p.min(), dist.p.max()))

# ---------------- 7. WHICH VARIABLE IS MOST ASSOCIATED WITH STUNTING? (Cramer's V, unweighted) ----------------
def cramers_v(a, b):
    t = pd.crosstab(a, b); chi2 = chi2_contingency(t)[0]; n = t.values.sum()
    return np.sqrt(chi2 / (n * (min(t.shape) - 1)))
d = df.dropna(subset=["stunted"])
cv = pd.Series({c: cramers_v(d[c], d.stunted) for c in ["age_group", "wealth_quintile", "mother_edu", "state", "caste",
                                                         "residence", "sex", "birth_season", "low_birth_wt"] if c in d}).sort_values(ascending=False)
print("\n=== Strength of association with stunting (Cramer's V: 0 = none, 1 = perfect) ===\n", cv.round(3).to_string())
plt.figure(figsize=(6, 4)); sns.barplot(x=cv.values, y=cv.index, color="#4C72B0"); plt.xlabel("Cramer's V"); plt.title("Association with stunting"); save("18_association_strength")
