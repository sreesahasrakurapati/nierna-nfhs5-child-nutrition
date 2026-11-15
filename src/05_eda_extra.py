"""PERSON B - extra EDA: only analyses NOT already in 03_eda.py.  Input: nfhs5_features.csv -> charts 17-22
17 univariate numeric | 18 univariate categorical | 19 three indicators by wealth
20 state stunting with uncertainty | 21 sex gap by age | 22 strength of association with stunting"""
from common import *
from scipy.stats import chi2_contingency

df = pd.read_csv(FEATURES)
need = ["stunted","wasted","underweight","sample_wt","state","district_code","age_months","age_group","sex","residence",
        "wealth_quintile","mother_edu","caste","weight_kg","height_cm","birth_weight_g"]
gone = [c for c in need if c not in df.columns]
if gone: raise SystemExit(f"These columns are missing from the features file: {gone}. Tell the owner of 01/02 before continuing.")
W  = ["Poorest","Poorer","Middle","Richer","Richest"]
AG = ["0-5","6-11","12-23","24-35","36-47","48-59"]
RED, BLUE, ORANGE, GREY = "#C0392B", "#1F4E79", "#E08E0B", "#8C8C8C"
SRC = "Source: NFHS-5 (2019-21)."
def finish(name, note=SRC):
    plt.gcf().text(0.01, 0.005, note, fontsize=8, color=GREY); plt.tight_layout(rect=(0, 0.03, 1, 1)); save(name)

# ---- 17. Univariate: numeric variables (cleaned data) ----
num = {"age_months":"Age (months)","weight_kg":"Weight (kg)","height_cm":"Height (cm)","birth_weight_g":"Birth weight (g)"}
print("=== Numeric variables ===")
print(df[list(num)].describe().round(1).T[["count","mean","50%","min","max"]].assign(skew=df[list(num)].skew().round(2)).to_string())
fig, ax = plt.subplots(1, 4, figsize=(16, 3.8))
for a, (c, t) in zip(ax, num.items()):
    a.hist(df[c].dropna(), bins=50, color=BLUE); a.set_title(t, fontsize=11); a.spines[["top","right"]].set_visible(False)
ax[0].set_ylabel("Number of children"); fig.suptitle("Age, weight, height and birth weight: what the children look like (cleaned data)", x=0.01, ha="left", fontweight="bold")
finish("17_univariate_numeric")

# ---- 18. Univariate: categorical variables ----
cats = {"sex":["Male","Female"], "residence":["Rural","Urban"], "wealth_quintile":W,
        "mother_edu":["No education","Primary","Secondary","Higher"], "caste":["SC","ST","OBC","General/None","Not recorded"]}
print("\n=== Category shares (% of children, unweighted) ===")
fig, ax = plt.subplots(1, 5, figsize=(18, 3.8))
for a, (c, order) in zip(ax, cats.items()):
    vc = (df[c].value_counts(normalize=True) * 100).reindex(order); print(c, vc.round(1).to_dict())
    a.bar(vc.index, vc.values, color=BLUE); a.set_title(c, fontsize=11); a.tick_params(axis="x", rotation=40); a.spines[["top","right"]].set_visible(False)
    for i, v in enumerate(vc.values): a.text(i, v + 0.8, f"{v:.0f}%", ha="center", fontsize=8)
rural = (df.residence == "Rural").mean() * 100
fig.suptitle(f"Who is in the sample: about {rural:.0f}% of children live in rural households (counts, not weighted)", x=0.01, ha="left", fontweight="bold")
finish("18_univariate_categorical")

# ---- 19. Three indicators by wealth ----
ind = pd.DataFrame({c: prev(df, "wealth_quintile", c) for c in ["stunted","wasted","underweight"]}).reindex(W)
print("\n=== Indicators by wealth (weighted %) ===\n", ind.round(1).to_string())
gap = ind.loc["Poorest"] - ind.loc["Richest"]
fig, ax = plt.subplots(figsize=(8.5, 4.6)); x = np.arange(len(W)); w = 0.27
for k, (c, lab, col) in enumerate([("stunted","Stunting",RED), ("wasted","Wasting",ORANGE), ("underweight","Underweight",BLUE)]):
    b = ax.bar(x + (k - 1) * w, ind[c], w, label=lab, color=col)
    ax.bar_label(b, labels=[f"{v:.0f}" for v in ind[c]], fontsize=8, padding=2)
ax.set_xticks(x); ax.set_xticklabels(W); ax.set_ylabel("% of children"); ax.legend(frameon=False); ax.spines[["top","right"]].set_visible(False)
ax.set_title(f"Poorest vs richest gap: {gap.stunted:.0f} points for stunting, {gap.underweight:.0f} for underweight, only {gap.wasted:.0f} for wasting", loc="left", fontsize=11, fontweight="bold")
finish("19_indicators_by_wealth", SRC + " Survey-weighted.")

# ---- 20. State stunting with approximate 95% intervals ----
def p_ci(g, col="stunted"):
    m = g[col].notna(); x, wt = g.loc[m, col], g.loc[m, "sample_wt"]
    p = np.average(x, weights=wt); neff = wt.sum() ** 2 / (wt ** 2).sum()
    return pd.Series({"p": p * 100, "ci": 1.96 * np.sqrt(p * (1 - p) / neff) * 100, "n": int(m.sum())})
st = df.groupby("state").apply(p_ci, include_groups=False).sort_values("p")
print("\n=== Widest state intervals (least certain) ===\n", st.sort_values("ci", ascending=False).head(5).round(1).to_string())
wide = st.sort_values("ci", ascending=False).index[:2]
fig, ax = plt.subplots(figsize=(7.5, 9.5)); ax.barh(st.index, st.p, xerr=st.ci, color=RED, ecolor="black", capsize=2)
ax.set_xlabel("Stunting % (bars = approximate 95% interval)"); ax.spines[["top","right"]].set_visible(False)
ax.set_title(f"Small places are less certain, e.g. {wide[0]} and {wide[1]}", loc="left", fontsize=12, fontweight="bold")
finish("20_state_stunting_uncertainty", SRC + " Intervals are approximate and ignore survey clustering, so true ranges are wider.")

# ---- 21. Sex gap by age group ----
sex = df.groupby(["age_group","sex"]).apply(lambda g: wmean(g, "stunted"), include_groups=False).unstack().reindex(AG)
print("\n=== Stunting % by age group and sex ===\n", sex.round(1).to_string(), "\nOverall:", prev(df, "sex").round(1).to_dict())
fig, ax = plt.subplots(figsize=(8.5, 4.6)); x = np.arange(len(AG)); w = 0.38
b1 = ax.bar(x - w/2, sex["Male"], w, color=BLUE, label="Boys"); b2 = ax.bar(x + w/2, sex["Female"], w, color=ORANGE, label="Girls")
for b in (b1, b2): ax.bar_label(b, labels=[f"{v:.0f}" for v in b.datavalues], fontsize=8, padding=2)
ax.set_xticks(x); ax.set_xticklabels(AG); ax.set_xlabel("Age group (months)"); ax.set_ylabel("Stunting (% of children)"); ax.legend(frameon=False, loc="upper left")
ax.spines[["top","right"]].set_visible(False)
under2 = (sex.loc[["6-11","12-23"], "Male"] > sex.loc[["6-11","12-23"], "Female"]).all()
ax.set_title("Boys are more stunted under age 2; the gap is small or reversed later" if under2 else "Stunting by age group and sex", loc="left", fontsize=12, fontweight="bold")
finish("21_sex_gap", SRC + " Survey-weighted.")

# ---- 22. Strength of association with stunting (Cramer's V) ----
def cramers_v(a, b):
    t = pd.crosstab(a, b); chi2 = chi2_contingency(t)[0]; n = t.values.sum()
    return np.sqrt(chi2 / (n * (min(t.shape) - 1)))
d = df.dropna(subset=["stunted"])
cv = pd.Series({c: cramers_v(d[c], d.stunted) for c in ["age_group","wealth_quintile","mother_edu","state","caste","residence","sex","birth_season","low_birth_wt"] if c in d}).sort_values()
print("\n=== Association with stunting (Cramer's V, 0 = none, 1 = perfect; unweighted) ===\n", cv.sort_values(ascending=False).round(3).to_string())
fig, ax = plt.subplots(figsize=(7, 4.4)); ax.barh(cv.index, cv.values, color=BLUE); ax.bar_label(ax.containers[0], labels=[f"{v:.2f}" for v in cv.values], fontsize=8, padding=2)
ax.set_xlabel("Cramer's V"); ax.spines[["top","right"]].set_visible(False)
ax.set_title("How strongly each factor is linked with stunting (all links are modest)", loc="left", fontsize=11, fontweight="bold")
finish("22_association_strength", SRC + " Unweighted. A link does not prove a cause.")

# ---- printed only (no chart): urban/rural after wealth, birth season, district range ----
ur = df.groupby(["wealth_quintile","residence"]).apply(lambda g: wmean(g, "stunted"), include_groups=False).unstack().reindex(W)
print("\nRural minus urban stunting gap within each wealth group:\n", (ur.Rural - ur.Urban).round(1).to_string())
print("\nStunting % by birth season:", prev(df, "birth_season").round(1).to_dict() if "birth_season" in df else "n/a")
dist = df.groupby(["state","district_code"]).apply(p_ci, include_groups=False).reset_index(); dist = dist[dist.n >= 100]
print("\nDistricts with >=100 children:", len(dist), "| stunting range: %.1f%% to %.1f%%" % (dist.p.min(), dist.p.max()))
