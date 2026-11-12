"""PERSON B - exploratory analysis.  Input: nfhs5_features.csv  ->  figures 03-06 and 09-14 in reports/figures"""
from common import *
from matplotlib.ticker import PercentFormatter

# ---------- team theme (local to this script so common.py is untouched) ----------
BLUE, RED, GREY, GREEN = "#1F5A8A", "#C0392B", "#8C8C8C", "#2E7D5B"
plt.rcParams.update({"font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
                     "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": False, "figure.facecolor": "white"})
SRC = "Source: NFHS-5 (2019-21), children under 5."

def finish(name, title, sub=None, w=False):
    plt.suptitle(title, x=0.01, ha="left", fontsize=13, fontweight="bold", wrap=True)
    plt.figtext(0.01, 0.005, (sub + "  |  " if sub else "") + SRC + (" Survey-weighted." if w else " Unweighted."), fontsize=8, color=GREY, ha="left")
    plt.tight_layout(rect=(0, 0.03, 1, 0.94)); plt.savefig(FIG / f"{name}.png", dpi=150); plt.close()

def bars(ax, labels, vals, color=BLUE, hi=None):
    cols = [color] * len(vals)
    if hi is not None: cols[hi] = RED
    b = ax.bar(labels, vals, color=cols)
    for r, v in zip(b, vals): ax.text(r.get_x() + r.get_width()/2, v + .6, f"{v:.0f}%", ha="center", fontsize=10)
    ax.set_ylim(0, max(vals) * 1.18); ax.yaxis.set_major_formatter(PercentFormatter(decimals=0)); ax.tick_params(axis="x", rotation=25)

df = pd.read_csv(FEATURES)
AG = ["0-5","6-11","12-23","24-35","36-47","48-59"]
df["age_group"] = pd.Categorical(df.age_group, AG, ordered=True)
WQ = ["Poorest","Poorer","Middle","Richer","Richest"]
ED = ["No education","Primary","Secondary","Higher"]

# 03. age curve -------------------------------------------------------------
age = df.groupby("age_months")[["haz","waz","whz"]].mean()
fig, ax = plt.subplots(figsize=(8.5, 4.5))
for c, col, lab in [("haz", RED, "Height-for-age (stunting)"), ("waz", BLUE, "Weight-for-age"), ("whz", GREEN, "Weight-for-height")]:
    ax.plot(age.index, age[c], color=col, lw=2, label=lab)
ax.axhline(-2, color="black", ls="--", lw=1); ax.text(59, -1.97, "-2 = malnourished cut-off", ha="right", va="bottom", fontsize=9)
ax.axvline(12, color=GREY, ls=":"); ax.set_xlabel("Age (months)"); ax.set_ylabel("Mean z-score"); ax.legend(frameon=False)
finish("03_age_curve", "Height falls behind sharply after the first birthday")
print("Stunting by age group:\n", prev(df, "age_group").round(1))

# 04. state ranking ---------------------------------------------------------
st = prev(df, "state").sort_values(); nat = wmean(df, "stunted")
fig, ax = plt.subplots(figsize=(8, 10))
ax.barh(st.index, st.values, color=[RED if v > nat else BLUE for v in st.values])
ax.axvline(nat, color="black", ls="--", lw=1); ax.text(nat + .3, 0, f"India {nat:.1f}%", fontsize=9)
for i, v in enumerate(st.values): ax.text(v + .3, i, f"{v:.0f}", va="center", fontsize=8)
ax.xaxis.set_major_formatter(PercentFormatter(decimals=0)); ax.set_xlabel("Children stunted")
finish("04_state_stunting", f"Stunting ranges from {st.min():.0f}% ({st.idxmin()}) to {st.max():.0f}% ({st.idxmax()})", "Red = above national average", w=True)

# 05. socio-economic gradients ---------------------------------------------
fig, ax = plt.subplots(1, 4, figsize=(16, 4.4), sharey=True)
specs = [("wealth_quintile", WQ, "Household wealth"), ("mother_edu", ED, "Mother's education"),
         ("residence", ["Rural","Urban"], "Residence"), ("caste", ["ST","SC","OBC","General/None","Not recorded"], "Caste group")]
for a, (by, order, t) in zip(ax, specs):
    p = prev(df, by).reindex(order); bars(a, order, p.values, hi=int(np.argmax(p.values))); a.set_title(t)
ax[0].set_ylabel("Children stunted")
finish("05_socio_gradients", "Stunting falls steadily with wealth and mother's education", w=True)

# 06. correlation (Spearman = robust to skew/outliers) ----------------------
num = ["haz","waz","whz","baz","age_months","weight_kg","height_cm","birth_weight_g","wealth_rank","edu_rank","birth_order_idx"]
plt.figure(figsize=(9, 7)); sns.heatmap(df[num].corr(method="spearman"), annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, annot_kws={"size": 8})
finish("06_corr", "Which variables move together? (Spearman correlation)", "z-scores overlap heavily with each other, so they are redundant")

# 09. distributions before vs after cleaning -------------------------------
raw = pd.read_csv(RAW, usecols=["hw70", "hw3", "m19"])
fig, ax = plt.subplots(2, 3, figsize=(14, 7))
ax[0, 0].hist(raw.hw70, bins=80, color=GREY); ax[0, 0].set_title("Height z-score, raw")
ax[0, 1].hist(raw.hw3, bins=80, color=GREY); ax[0, 1].set_title("Height, raw (mm)")
ax[0, 2].hist(raw.m19, bins=80, color=GREY); ax[0, 2].set_title("Birth weight, raw (g)")
ax[1, 0].hist(df.haz.dropna(), bins=80, color=BLUE); ax[1, 0].axvline(-2, color=RED, ls="--"); ax[1, 0].set_title("Height z-score, cleaned")
ax[1, 1].hist(df.height_cm.dropna(), bins=80, color=BLUE); ax[1, 1].set_title("Height (cm), cleaned")
ax[1, 2].hist(df.birth_weight_g.dropna(), bins=80, color=BLUE); ax[1, 2].axvline(2500, color=RED, ls="--"); ax[1, 2].set_title("Birth weight (g), cleaned")
finish("09_dist_before_after", "Special codes (spike at 9999) distort raw data; cleaning fixes it", "Top: raw. Bottom: cleaned. Birth weight clusters at 2000/2500/3000 g (rounded reports)")

# 10. z-score distributions by wealth (distribution shift) -----------------
fig, ax = plt.subplots(figsize=(8.5, 4.5))
for q, col in [("Poorest", RED), ("Richest", BLUE)]:
    sns.kdeplot(df.loc[df.wealth_quintile == q, "haz"].dropna(), ax=ax, color=col, lw=2, fill=True, alpha=.2, label=q)
ax.axvline(-2, color="black", ls="--"); ax.set_xlabel("Height-for-age z-score"); ax.legend(frameon=False, title="Wealth")
finish("10_haz_by_wealth", "The whole height distribution shifts left for the poorest children")

# 11. age x wealth ------------------------------------------------------------
t = df[df.wealth_quintile.isin(["Poorest", "Richest"])]
p = t.groupby(["age_group", "wealth_quintile"], observed=True).apply(lambda g: wmean(g, "stunted"), include_groups=False).unstack()
fig, ax = plt.subplots(figsize=(8.5, 4.5))
ax.plot(AG, p.loc[AG, "Poorest"], "o-", color=RED, lw=2, label="Poorest"); ax.plot(AG, p.loc[AG, "Richest"], "o-", color=BLUE, lw=2, label="Richest")
for x in AG: ax.text(x, p.loc[x, "Poorest"] + 1.2, f"{p.loc[x, 'Poorest']:.0f}%", ha="center", fontsize=9); ax.text(x, p.loc[x, "Richest"] - 3.2, f"{p.loc[x, 'Richest']:.0f}%", ha="center", fontsize=9)
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0)); ax.set_ylim(10, 60); ax.set_xlabel("Age group (months)"); ax.set_ylabel("Children stunted"); ax.legend(frameon=False)
finish("11_age_by_wealth", f"The wealth gap opens after infancy: {p.loc['12-23','Poorest']-p.loc['12-23','Richest']:.0f} points by 12-23 months", w=True)
print("Poorest vs richest by age:\n", p.round(1))

# 12. wealth x education ----------------------------------------------------
w = df.copy(); w["wealth3"] = w.wealth_quintile.map({"Poorest": "Poor", "Poorer": "Poor", "Middle": "Middle", "Richer": "Rich", "Richest": "Rich"})
h = w.groupby(["wealth3", "mother_edu"]).apply(lambda g: wmean(g, "stunted"), include_groups=False).unstack().reindex(index=["Poor", "Middle", "Rich"], columns=ED)
plt.figure(figsize=(7.5, 4.5)); sns.heatmap(h, annot=True, fmt=".0f", cmap="Reds", cbar_kws={"label": "% stunted"})
plt.ylabel("Household wealth"); plt.xlabel("Mother's education")
finish("12_wealth_by_education", f"Both matter: {h.loc['Poor','No education']:.0f}% stunted for poor + uneducated mother, {h.loc['Rich','Higher']:.0f}% for rich + higher education", w=True)

# 13. rural/urban gap within wealth ----------------------------------------
r = df.groupby(["wealth_quintile", "residence"]).apply(lambda g: wmean(g, "stunted"), include_groups=False).unstack().reindex(WQ)
fig, ax = plt.subplots(figsize=(8.5, 4.5)); x = np.arange(5)
ax.bar(x - .2, r["Rural"], .4, color=GREEN, label="Rural"); ax.bar(x + .2, r["Urban"], .4, color=BLUE, label="Urban")
ax.set_xticks(x, WQ); ax.yaxis.set_major_formatter(PercentFormatter(decimals=0)); ax.legend(frameon=False); ax.set_ylabel("Children stunted")
finish("13_rural_urban_within_wealth", "Within the same wealth level, the rural-urban gap is small", w=True)
print("Rural vs urban by wealth:\n", r.round(1))

# 14. multiple failures ------------------------------------------------------
n = df.dropna(subset=["n_failures"]).groupby("n_failures").sample_wt.sum(); n = n / n.sum() * 100
fig, ax = plt.subplots(figsize=(7, 4.2)); bars(ax, ["None", "1", "2", "All 3"], n.values, hi=None); ax.tick_params(axis="x", rotation=0)
ax.set_xlabel("Number of failures (stunted, wasted, underweight)")
finish("14_failure_combinations", f"{n.loc[2:].sum():.0f}% of children have two or more forms of malnutrition", w=True)

# ---------- extra checks (printed for the notes) ----------
tmp = df.dropna(subset=["low_birth_wt"])
print("Stunting by low-birth-weight:", prev(tmp, "low_birth_wt").round(1).to_dict())
print("Stunting by birth-weight recorded:", prev(df, "bw_recorded").round(1).to_dict())
print("Stunting by sex:", prev(df, "sex").round(1).to_dict())
print("Stunting by birth season:", prev(df, "birth_season").round(1).to_dict())

# outliers within age month (kept, not deleted: they are real short/thin children)
def iqr_flag(g, c):
    q1, q3 = g[c].quantile([.25, .75]); i = q3 - q1
    return (g[c] < q1 - 1.5*i) | (g[c] > q3 + 1.5*i)
out = df.groupby("age_months", group_keys=False).apply(lambda g: iqr_flag(g, "height_cm"), include_groups=False)
print("height outliers within age:", int(out.sum()))
